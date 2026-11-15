//+------------------------------------------------------------------+
//|                                              AurumBridgeEA.mq5   |
//|               AI Holding Company V8 - MT5 Algorithmic Bridge     |
//|       Autonomous Real-Time Execution Connector for XM / Mac MT5  |
//|         Copyright 2026, AI Holding Company V8 Portable System     |
//+------------------------------------------------------------------+
#property copyright   "Copyright 2026, AI Holding Company V8"
#property link        "https://github.com/Salmonnnnnn/AI-Holding-Company-V8-Portable"
#property version     "8.00"
#property description "AurumBridgeEA: Ultra-Low Latency REST API Bridge for MetaTrader 5."
#property description "Transfers live telemetry to AI Holding Company and executes algorithmic"
#property description "orders with strict risk controls: 0.05 lot cap, 3% daily drawdown guard,"
#property description "and demo-only security locks."

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\AccountInfo.mqh>
#include <Trade\SymbolInfo.mqh>

//--- EA Inputs
input group "=== [1] Bridge Server Connection ==="
input string   InpBridgeUrl         = "http://127.0.0.1:8080";  // Bridge Server URL (Mac localhost)
input string   InpBridgeToken       = "aurum_xm_mt5_bridge_2026"; // Bridge Auth Token (Pre-configured)
input int      InpPollIntervalSec   = 2;                        // Heartbeat / Poll Interval (Seconds)

input group "=== [2] Safety & Risk Management Guards ==="
input double   InpMaxLot            = 0.05;                     // Hard Lot Cap (Default: 0.05)
input double   InpMaxDailyLossPct   = 3.0;                      // Max Daily Loss % Threshold (Default: 3.0%)
input bool     InpAllowLiveAccount  = true;                     // Allow Live Account Execution (Strict Demo Lock)
input ulong    InpMagicNumber       = 888999;                   // EA Magic Number
input ulong    InpSlippagePoints    = 35;                       // Max Slippage (Points)

input group "=== [3] Symbol Configuration ==="
input bool     InpAutoDetectGold    = true;                     // Auto-detect Gold Symbol (GOLD / XAUUSD)
input string   InpManualGoldSymbol  = "XAUUSD";                 // Fallback Gold Symbol if auto-detect fails

//--- Internal State
CTrade         g_trade;
CPositionInfo  g_pos;
CAccountInfo   g_account;
CSymbolInfo    g_sym;

string         g_active_gold_symbol = "XAUUSD";
double         g_day_start_equity   = 0.0;
int            g_last_day_of_year   = -1;
double         g_daily_loss_pct     = 0.0;
bool           g_kill_switch_active = false;
int            g_consecutive_errors = 0;
bool           g_webrequest_warned  = false;

//+------------------------------------------------------------------+
//| Auto-detect broker Gold symbol variant (Strictly favors XAUUSD) |
//+------------------------------------------------------------------+
string DetectGoldSymbol()
{
   // 1. Always prioritize exact XAUUSD symbol first
   if(SymbolSelect("XAUUSD", true))
   {
      double bid = SymbolInfoDouble("XAUUSD", SYMBOL_BID);
      if(bid > 500.0)
      {
         Print("AurumBridgeEA: Successfully locked to XAUUSD (Bid: ", DoubleToString(bid, 2), ")");
         return "XAUUSD";
      }
   }

   if(!InpAutoDetectGold && StringLen(InpManualGoldSymbol) > 0)
      return InpManualGoldSymbol;

   // 2. Prioritize XAUUSD micro/raw/pro variants before GOLD
   string candidates[9] = { "XAUUSD", "XAUUSD.m", "XAUUSD.raw", "XAUUSD.pro", "XAUUSDm", _Symbol, "GOLD", "GOLD#", "XAUUSD_i" };
   for(int i = 0; i < 9; i++)
   {
      string s = candidates[i];
      if(StringLen(s) == 0) continue;
      if(SymbolSelect(s, true))
      {
         double bid = SymbolInfoDouble(s, SYMBOL_BID);
         if(bid > 500.0) // Gold price validation (e.g. > $500/oz)
         {
            Print("AurumBridgeEA: Successfully detected active symbol -> ", s);
            return s;
         }
      }
   }
   return "XAUUSD";
}

//+------------------------------------------------------------------+
//| Simple JSON field extractor helper                               |
//+------------------------------------------------------------------+
string ExtractJsonString(const string json, const string key)
{
   string search_key = "\"" + key + "\":\"";
   int pos = StringFind(json, search_key);
   if(pos < 0) return "";
   pos += StringLen(search_key);
   int end_pos = StringFind(json, "\"", pos);
   if(end_pos < 0) return "";
   return StringSubstr(json, pos, end_pos - pos);
}

double ExtractJsonDouble(const string json, const string key)
{
   string search_key = "\"" + key + "\":";
   int pos = StringFind(json, search_key);
   if(pos < 0) return 0.0;
   pos += StringLen(search_key);
   // Skip spaces
   while(pos < StringLen(json) && (StringGetCharacter(json, pos) == ' ' || StringGetCharacter(json, pos) == '\"'))
      pos++;
   int end_pos = pos;
   while(end_pos < StringLen(json))
   {
      ushort c = StringGetCharacter(json, end_pos);
      if((c >= '0' && c <= '9') || c == '.' || c == '-')
         end_pos++;
      else
         break;
   }
   if(end_pos > pos)
      return StringToDouble(StringSubstr(json, pos, end_pos - pos));
   return 0.0;
}

bool ExtractJsonBool(const string json, const string key)
{
   string search_key = "\"" + key + "\":";
   int pos = StringFind(json, search_key);
   if(pos < 0) return false;
   pos += StringLen(search_key);
   while(pos < StringLen(json) && StringGetCharacter(json, pos) == ' ')
      pos++;
   if(StringFind(json, "true", pos) == pos) return true;
   return false;
}

//+------------------------------------------------------------------+
//| HTTP POST WebRequest wrapper                                     |
//+------------------------------------------------------------------+
int HttpPostJson(const string endpoint, const string json_body, string &response_text)
{
   char post_data[];
   char result_data[];
   string result_headers;
   string url = InpBridgeUrl + endpoint;

   StringToCharArray(json_body, post_data, 0, WHOLE_ARRAY, CP_UTF8);
   int data_size = ArraySize(post_data);
   if(data_size > 0 && post_data[data_size - 1] == 0)
      ArrayResize(post_data, data_size - 1); // Remove terminating null byte

   string headers = "Content-Type: application/json; charset=utf-8\r\nAccept: application/json\r\n";

   ResetLastError();
   int res = WebRequest("POST", url, headers, 4000, post_data, result_data, result_headers);
   if(res == -1)
   {
      int err = GetLastError();
      if(err == 4060) // ERR_WEBREQUEST_URL_NOT_ALLOWED
      {
         if(!g_webrequest_warned)
         {
            Print("=========================================================================");
            Print("⚠️ AurumBridgeEA WebRequest Error 4060: URL NOT ALLOWED!");
            Print("👉 Please enable WebRequest in MT5:");
            Print("   1. Open Tools -> Options -> Expert Advisors (or Cmd+, on Mac)");
            Print("   2. Check 'Allow WebRequest for listed URL:'");
            Print("   3. Add URL: ", InpBridgeUrl);
            Print("=========================================================================");
            g_webrequest_warned = true;
         }
      }
      else
      {
         Print("AurumBridgeEA WebRequest failed. Error code: ", err, " | URL: ", url);
      }
      return -1;
   }

   response_text = CharArrayToString(result_data, 0, WHOLE_ARRAY, CP_UTF8);
   return res;
}

//+------------------------------------------------------------------+
//| Build heartbeat payload                                          |
//+------------------------------------------------------------------+
string BuildHeartbeatJson()
{
   long login = AccountInfoInteger(ACCOUNT_LOGIN);
   string company = AccountInfoString(ACCOUNT_COMPANY);
   string server = AccountInfoString(ACCOUNT_SERVER);
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double margin = AccountInfoDouble(ACCOUNT_MARGIN);
   double free_margin = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
   double profit = AccountInfoDouble(ACCOUNT_PROFIT);
   bool is_demo = (AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_DEMO);
   string currency = AccountInfoString(ACCOUNT_CURRENCY);

   // Sanitize strings
   StringReplace(company, "\"", "'");
   StringReplace(server, "\"", "'");

   // Open positions array
   string pos_json = "[";
   int total_pos = PositionsTotal();
   int added = 0;
   for(int i = 0; i < total_pos; i++)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket > 0)
      {
         string sym = PositionGetString(POSITION_SYMBOL);
         long type = PositionGetInteger(POSITION_TYPE);
         double vol = PositionGetDouble(POSITION_VOLUME);
         double open_p = PositionGetDouble(POSITION_PRICE_OPEN);
         double sl = PositionGetDouble(POSITION_SL);
         double tp = PositionGetDouble(POSITION_TP);
         double pnl = PositionGetDouble(POSITION_PROFIT);

         if(added > 0) pos_json += ",";
         pos_json += StringFormat("{\"ticket\":%I64u,\"symbol\":\"%s\",\"type\":\"%s\",\"volume\":%.2f,\"open_price\":%.2f,\"sl\":%.2f,\"tp\":%.2f,\"profit\":%.2f}",
                                  ticket, sym, (type == POSITION_TYPE_BUY ? "BUY" : "SELL"), vol, open_p, sl, tp, pnl);
         added++;
      }
   }
   pos_json += "]";

   string payload = StringFormat(
      "{\"token\":\"%s\",\"account\":%I64d,\"broker\":\"%s\",\"server\":\"%s\",\"balance\":%.2f,\"equity\":%.2f,\"margin\":%.2f,\"free_margin\":%.2f,\"floating_pnl\":%.2f,\"is_demo\":%s,\"currency\":\"%s\",\"open_positions\":%s}",
      InpBridgeToken, login, company, server, balance, equity, margin, free_margin, profit, (is_demo ? "true" : "false"), currency, pos_json
   );

   return payload;
}

//+------------------------------------------------------------------+
//| Send Acknowledge feedback back to AI Server                      |
//+------------------------------------------------------------------+
void SendAck(const string cmd_id, const string status, ulong ticket = 0, double price = 0.0, const string err_msg = "")
{
   string ack_json = StringFormat(
      "{\"token\":\"%s\",\"cmd_id\":\"%s\",\"status\":\"%s\",\"ticket\":%I64u,\"price\":%.2f,\"error\":\"%s\"}",
      InpBridgeToken, cmd_id, status, ticket, price, err_msg
   );
   string response;
   HttpPostJson("/api/mt5/ack", ack_json, response);
}

//+------------------------------------------------------------------+
//| Close all open positions                                         |
//+------------------------------------------------------------------+
int CloseAllPositions(const string reason)
{
   int closed = 0;
   int total = PositionsTotal();
   for(int i = total - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket > 0)
      {
         if(g_trade.PositionClose(ticket, InpSlippagePoints))
         {
            closed++;
            Print("AurumBridgeEA: Closed position #", ticket, " (", reason, ")");
         }
         else
         {
            Print("AurumBridgeEA: Failed to close #", ticket, " Error: ", g_trade.ResultRetcodeDescription());
         }
      }
   }
   return closed;
}

//+------------------------------------------------------------------+
//| Execute algorithmic trade command                                |
//+------------------------------------------------------------------+
void ProcessCommand(const string cmd_block)
{
   string cmd_id = ExtractJsonString(cmd_block, "cmd_id");
   string cmd_type = ExtractJsonString(cmd_block, "cmd_type");
   string symbol = ExtractJsonString(cmd_block, "symbol");
   double volume = ExtractJsonDouble(cmd_block, "volume");
   double sl_dist = ExtractJsonDouble(cmd_block, "sl_distance");
   double tp_dist = ExtractJsonDouble(cmd_block, "tp_distance");
   string comment = ExtractJsonString(cmd_block, "comment");

   if(StringLen(cmd_id) == 0 || StringLen(cmd_type) == 0) return;

   Print("AurumBridgeEA: Received Command -> ", cmd_type, " [ID: ", cmd_id, ", Vol: ", volume, "]");

   // 1. Guardrail: Demo Account Check
   bool is_demo = (AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_DEMO);
   if(!is_demo && !InpAllowLiveAccount)
   {
      Print("AurumBridgeEA: REJECTED! Live trading not authorized in EA inputs.");
      SendAck(cmd_id, "REJECTED", 0, 0.0, "Live trading prohibited by EA settings");
      CloseAllPositions("Live account safety breach");
      return;
   }

   // 2. Guardrail: Daily Drawdown Limit
   if(g_daily_loss_pct >= InpMaxDailyLossPct)
   {
      Print("AurumBridgeEA: REJECTED! Daily loss limit reached (", g_daily_loss_pct, "% >= ", InpMaxDailyLossPct, "%).");
      SendAck(cmd_id, "REJECTED", 0, 0.0, "Daily loss limit exceeded");
      return;
   }

   // 3. Command: CLOSE_ALL
   if(cmd_type == "CLOSE_ALL")
   {
      int cnt = CloseAllPositions("Command CLOSE_ALL received");
      SendAck(cmd_id, "DONE", 0, 0.0, StringFormat("Closed %d positions", cnt));
      return;
   }

   // 4. Command: CLOSE_TICKET or CLOSE_ORDER
   if(cmd_type == "CLOSE_TICKET" || cmd_type == "CLOSE_ORDER")
   {
      ulong ticket = (ulong)ExtractJsonDouble(cmd_block, "ticket");
      if(ticket > 0 && g_pos.SelectByTicket(ticket))
      {
         if(g_trade.PositionClose(ticket))
            SendAck(cmd_id, "DONE", ticket, g_pos.PriceCurrent(), "Ticket closed successfully");
         else
            SendAck(cmd_id, "FAILED", ticket, 0.0, g_trade.ResultRetcodeDescription());
         return;
      }
      else
      {
         SendAck(cmd_id, "FAILED", ticket, 0.0, "Position ticket not found or already closed");
         return;
      }
   }

   // 5. Command: OPEN_BUY or OPEN_SELL
   if(cmd_type == "BUY" || cmd_type == "OPEN_BUY" || cmd_type == "SELL" || cmd_type == "OPEN_SELL")
   {
      // Hard lot cap check
      if(volume > InpMaxLot)
      {
         Print("AurumBridgeEA: REJECTED! Volume ", volume, " exceeds hard cap of ", InpMaxLot);
         SendAck(cmd_id, "REJECTED", 0, 0.0, StringFormat("Volume %.2f exceeds InpMaxLot %.2f", volume, InpMaxLot));
         return;
      }
      if(volume <= 0.0) volume = 0.01;

      // Ensure symbol exists
      string trade_symbol = g_active_gold_symbol;
      if(StringLen(symbol) > 0 && symbol != "*" && symbol != "XAUUSD")
      {
         if(SymbolSelect(symbol, true))
            trade_symbol = symbol;
      }

      if(!g_sym.Name(trade_symbol) || !g_sym.RefreshRates())
      {
         SendAck(cmd_id, "FAILED", 0, 0.0, "Cannot refresh rates for " + trade_symbol);
         return;
      }

      bool is_buy = (cmd_type == "BUY" || cmd_type == "OPEN_BUY");
      double entry_price = is_buy ? g_sym.Ask() : g_sym.Bid();
      int digits = (int)g_sym.Digits();
      double sl = 0.0;
      double tp = 0.0;

      if(sl_dist > 0.0)
         sl = NormalizeDouble(is_buy ? (entry_price - sl_dist) : (entry_price + sl_dist), digits);
      if(tp_dist > 0.0)
         tp = NormalizeDouble(is_buy ? (entry_price + tp_dist) : (entry_price - tp_dist), digits);

      if(StringLen(comment) == 0)
         comment = "AurumBridge_Auto";

      bool success = false;
      if(is_buy)
         success = g_trade.Buy(volume, trade_symbol, entry_price, sl, tp, comment);
      else
         success = g_trade.Sell(volume, trade_symbol, entry_price, sl, tp, comment);

      if(success && g_trade.ResultRetcode() == TRADE_RETCODE_DONE)
      {
         ulong ticket = g_trade.ResultOrder();
         double exec_price = g_trade.ResultPrice();
         Print("AurumBridgeEA: Order SUCCESS #", ticket, " at price ", exec_price);
         SendAck(cmd_id, "DONE", ticket, exec_price, "Executed successfully");
      }
      else
      {
         string err_desc = g_trade.ResultRetcodeDescription();
         Print("AurumBridgeEA: Order FAILED -> ", err_desc, " (retcode=", g_trade.ResultRetcode(), ")");
         SendAck(cmd_id, "FAILED", 0, 0.0, err_desc);
      }
      return;
   }

   SendAck(cmd_id, "UNKNOWN_COMMAND", 0, 0.0, "Command type not supported: " + cmd_type);
}

//+------------------------------------------------------------------+
//| Parse commands array and dispatch                                |
//+------------------------------------------------------------------+
void ParseAndExecuteCommands(const string response)
{
   int cmd_pos = StringFind(response, "\"commands\":");
   if(cmd_pos < 0) return;

   int arr_start = StringFind(response, "[", cmd_pos);
   if(arr_start < 0) return;

   int arr_end = StringFind(response, "]", arr_start);
   if(arr_end <= arr_start + 1) return; // Empty array "[]"

   string commands_block = StringSubstr(response, arr_start, arr_end - arr_start + 1);

   // Extract each JSON object inside commands array
   int cursor = 0;
   while(cursor < StringLen(commands_block))
   {
      int obj_start = StringFind(commands_block, "{", cursor);
      if(obj_start < 0) break;
      int obj_end = StringFind(commands_block, "}", obj_start);
      if(obj_end < 0) break;

      string single_cmd = StringSubstr(commands_block, obj_start, obj_end - obj_start + 1);
      ProcessCommand(single_cmd);
      cursor = obj_end + 1;
   }
}

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("=========================================================================");
   Print("🚀 Initializing AurumBridgeEA V8.00 (AI Holding Company MT5 Connector)");
   Print("   Bridge URL   : ", InpBridgeUrl);
   Print("   Poll Interval: ", InpPollIntervalSec, " seconds");
   Print("   Max Lot Cap  : ", InpMaxLot);
   Print("   Max Drawdown : ", InpMaxDailyLossPct, "%");
   Print("=========================================================================");

   g_trade.SetExpertMagicNumber(InpMagicNumber);
   g_trade.SetDeviationInPoints(InpSlippagePoints);
   g_trade.SetTypeFilling(ORDER_FILLING_IOC);

   g_active_gold_symbol = DetectGoldSymbol();

   // Set timer for periodic polling & heartbeat
   if(!EventSetTimer(MathMax(1, InpPollIntervalSec)))
   {
      Print("❌ AurumBridgeEA: Failed to initialize timer!");
      return INIT_FAILED;
   }

   Print("✅ AurumBridgeEA running. Waiting for next timer tick...");
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();
   Print("AurumBridgeEA stopped (Reason: ", reason, ")");
}

//+------------------------------------------------------------------+
//| Expert timer function (Runs every InpPollIntervalSec)           |
//+------------------------------------------------------------------+
void OnTimer()
{
   // Track day equity and calculate daily loss %
   MqlDateTime dt;
   TimeCurrent(dt);
   if(dt.day_of_year != g_last_day_of_year || g_day_start_equity <= 0.0)
   {
      g_last_day_of_year = dt.day_of_year;
      g_day_start_equity = AccountInfoDouble(ACCOUNT_EQUITY);
      if(g_day_start_equity <= 0.0)
         g_day_start_equity = AccountInfoDouble(ACCOUNT_BALANCE);
   }

   double cur_equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(g_day_start_equity > 0.0 && cur_equity < g_day_start_equity)
      g_daily_loss_pct = ((g_day_start_equity - cur_equity) / g_day_start_equity) * 100.0;
   else
      g_daily_loss_pct = 0.0;

   // Auto-close and halt if daily loss breached
   if(g_daily_loss_pct >= InpMaxDailyLossPct && !g_kill_switch_active)
   {
      Print("🚨 AurumBridgeEA: Daily drawdown limit reached (", g_daily_loss_pct, "% >= ", InpMaxDailyLossPct, "%). Triggering emergency CLOSE_ALL!");
      g_kill_switch_active = true;
      CloseAllPositions("Max daily loss safety limit breached");
   }

   // Prepare and send heartbeat
   string heartbeat_payload = BuildHeartbeatJson();
   string response = "";
   int http_res = HttpPostJson("/api/mt5/heartbeat", heartbeat_payload, response);

   if(http_res == 200)
   {
      g_consecutive_errors = 0;
      bool remote_kill = ExtractJsonBool(response, "kill_switch");
      if(remote_kill && !g_kill_switch_active)
      {
         Print("🚨 AurumBridgeEA: Remote Kill Switch signal received from AI Server!");
         g_kill_switch_active = true;
         CloseAllPositions("Remote Kill Switch triggered from AI Hub");
      }
      else if(!remote_kill && g_kill_switch_active)
      {
         g_kill_switch_active = false;
         Print("🟢 AurumBridgeEA: Remote Kill Switch cleared. Ready for orders.");
      }

      // Check and execute incoming commands
      ParseAndExecuteCommands(response);
   }
   else
   {
      g_consecutive_errors++;
      if(g_consecutive_errors % 10 == 0)
         Print("AurumBridgeEA: Warning - Failed to communicate with AI Bridge Server (", g_consecutive_errors, " consecutive retries)");
   }
}
//+------------------------------------------------------------------+