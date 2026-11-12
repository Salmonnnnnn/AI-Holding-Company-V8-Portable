"""
MetaTrader 5 (MT5) Algorithmic Execution Bridge & Live Step-by-Step Demo Simulator (V4)
Provides:
1. Real MetaTrader 5 Python Connector (mt5.initialize, symbol_info_tick, order_send, TRADE_ACTION_SLTP)
2. Interactive 8-Step Live MT5 Demo Execution Simulator + Tick-by-Tick Trajectory for visual inspection.
"""
import os
from datetime import datetime


class MT5ExecutionBridge:
    def __init__(self):
        self.magic_number = 888999
        self.max_spread_points = 35
        self.mt5_symbol = os.getenv("MT5_SYMBOL", "XAUUSD")

    def build_mt5_order_request(self, direction: str, lot_size: float, entry_price: float, sl_price: float, tp_price: float) -> dict:
        """สร้างโครงสร้าง Dictionary มาตรฐานสำหรับส่งคำสั่ง mt5.order_send()"""
        return {
            "action": "mt5.TRADE_ACTION_DEAL (1)",
            "symbol": self.mt5_symbol,
            "volume": float(lot_size),
            "type": "mt5.ORDER_TYPE_BUY (0)" if "BUY" in direction.upper() else "mt5.ORDER_TYPE_SELL (1)",
            "price": round(float(entry_price), 2),
            "sl": round(float(sl_price), 2),
            "tp": round(float(tp_price), 2),
            "deviation": 20,
            "magic": self.magic_number,
            "comment": "AI_Virtual_Firm_V4_AutoBot",
            "type_time": "mt5.ORDER_TIME_GTC",
            "type_filling": "mt5.ORDER_FILLING_IOC"
        }

    def execute_real_mt5_if_available(self, direction: str, lot_size: float, sl_price: float, tp_price: float) -> dict:
        """เชื่อมต่อโปรแกรม MetaTrader 5 บนเครื่องจริง (เมื่อติดตั้งแพ็กเกจ MetaTrader5 และเปิดโปรแกรม MT5)"""
        try:
            import MetaTrader5 as mt5  # type: ignore
            if not mt5.initialize():
                return {"connected": False, "reason": f"mt5.initialize() failed: {mt5.last_error()}"}

            symbol_info = mt5.symbol_info(self.mt5_symbol)
            if symbol_info is None:
                mt5.shutdown()
                return {"connected": False, "reason": f"Symbol {self.mt5_symbol} not found on broker."}

            if not symbol_info.visible:
                mt5.symbol_select(self.mt5_symbol, True)

            tick = mt5.symbol_info_tick(self.mt5_symbol)
            is_buy = "BUY" in direction.upper()
            exec_price = tick.ask if is_buy else tick.bid
            order_type = mt5.ORDER_TYPE_BUY if is_buy else mt5.ORDER_TYPE_SELL

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.mt5_symbol,
                "volume": float(lot_size),
                "type": order_type,
                "price": exec_price,
                "sl": float(sl_price),
                "tp": float(tp_price),
                "deviation": 20,
                "magic": self.magic_number,
                "comment": "AI_Virtual_Firm_V4",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            result = mt5.order_send(request)
            mt5.shutdown()
            return {
                "connected": True,
                "retcode": result.retcode,
                "ticket": result.order,
                "price": exec_price
            }
        except Exception as e:
            return {"connected": False, "reason": str(e)}

    def simulate_live_mt5_demo_execution(self, cio_verdict: dict, market_data: dict, best_strategy_name: str) -> dict:
        """
        จำลองขั้นตอนการทำงานของบอทกับพอร์ต MT5 Demo แบบสดๆ ทีละขั้นตอน (8-Step Execution Telemetry)
        พร้อมสร้างชุดข้อมูลราคาวิ่งแบบ Tick-by-Tick 40 จุด เพื่อให้ผู้ใช้กดรันดูบนหน้าเว็บได้ทันที
        """
        action_raw = str(cio_verdict.get("action", "SELL (SHORT)"))
        direction = "BUY" if "BUY" in action_raw.upper() else "SELL"
        entry = round(float(cio_verdict.get("final_entry", market_data.get("current_price", 2685.0))), 2)
        sl = round(float(cio_verdict.get("final_sl", entry - 18.0 if direction == "BUY" else entry + 18.0)), 2)
        tp1 = round(float(cio_verdict.get("final_tp1", entry + 32.0 if direction == "BUY" else entry - 32.0)), 2)
        tp2 = round(float(cio_verdict.get("final_tp2", entry + 50.0 if direction == "BUY" else entry - 50.0)), 2)
        lot = float(cio_verdict.get("recommended_lot", 0.02))

        spread_pts = 18  # 18 points ($0.18 บนทองคำ ECN)
        bid_price = entry if direction == "SELL" else round(entry - 0.18, 2)
        ask_price = round(bid_price + 0.18, 2)

        sl_dist = abs(entry - sl)
        tp1_dist = abs(tp1 - entry)
        tp2_dist = abs(tp2 - entry)
        profit_tp1_half = round((tp1_dist * (lot * 0.5) * 100.0), 2)
        profit_tp2_half = round((tp2_dist * (lot * 0.5) * 100.0), 2)
        total_demo_profit = round(profit_tp1_half + profit_tp2_half, 2)

        # สร้างกราฟจำลอง Tick-by-Tick 36 จุด (จาก Entry -> ย่อทดสอบนิดหน่อย -> วิ่งชน TP1 ขยับ SL บังทุน -> วิ่งชน TP2)
        sign = 1.0 if direction == "BUY" else -1.0
        tick_series = []
        fractions = [
            0.0, -0.12, -0.22, -0.08, 0.05, 0.18, 0.32, 0.45, 0.38, 0.55,
            0.72, 0.88, 1.02, 1.08, 0.95, 1.15, 1.32, 1.48, 1.62, 1.75,
            1.68, 1.85, 2.02, 2.18, 2.35, 2.52, 2.68, 2.82
        ]
        for idx, frac in enumerate(fractions):
            p = round(entry + (sign * sl_dist * frac), 2)
            event_label = "TICK"
            if idx == 0:
                event_label = f"ORDER_OPEN ({direction} @ ${entry:,.2f})"
            elif idx == 12:
                p = tp1
                event_label = f"TP1_HIT (${tp1:,.2f}) -> AUTO BREAK-EVEN SL=${entry:,.2f}"
            elif idx == len(fractions) - 1:
                p = tp2
                event_label = f"TP2_HIT (${tp2:,.2f}) -> FULL PROFIT +${total_demo_profit:,.2f}"
            tick_series.append({
                "step": idx + 1,
                "price": p,
                "event": event_label
            })

        steps_log = [
            {
                "step": 1,
                "phase": "MT5_INITIALIZE & LOGIN",
                "code": "mt5.initialize() & mt5.login(account=50892104, server='MetaQuotes-Demo')",
                "detail": "เชื่อมต่อเทอร์มินัล MetaTrader 5 สำเร็จ (Ping: 14.2ms | Demo Balance: $10,000.00 | Leverage 1:200)",
                "status": "SUCCESS ✅"
            },
            {
                "step": 2,
                "phase": "SYMBOL_TICK & SPREAD GUARD",
                "code": f"tick = mt5.symbol_info_tick('{self.mt5_symbol}') # Bid={bid_price}, Ask={ask_price}",
                "detail": f"ตรวจค่า Spread ปัจจุบัน = {spread_pts} Points ($0.18/oz) ผ่านเกณฑ์ความปลอดภัย (<= {self.max_spread_points} Points)",
                "status": "PASSED ✅"
            },
            {
                "step": 3,
                "phase": "CENTRAL NEXUS SIGNAL INJECTION",
                "code": f"signal = nexus.get_cio_approved_setup(strategy='{best_strategy_name}')",
                "detail": f"ดึงแผนเทรดที่ผ่านการดีเบตและกลยุทธ์ '{best_strategy_name}' -> คำสั่ง {direction} @ ${entry:,.2f}",
                "status": "VERIFIED 🧠"
            },
            {
                "step": 4,
                "phase": "MARGIN & DYNAMIC LOT SIZING",
                "code": f"mt5.order_calc_margin(ORDER_TYPE_{direction}, '{self.mt5_symbol}', {lot}, {entry})",
                "detail": f"คำนวณขนาดออเดอร์ {lot} Lot (ระยะ SL ${sl_dist:.2f}, R:R 1:1.8 / 1:2.8) ใช้ Margin เพียง $39.08",
                "status": "CALCULATED 🛡️"
            },
            {
                "step": 5,
                "phase": "MT5 ORDER_SEND EXECUTION",
                "code": f"mt5.order_send({{'action': TRADE_ACTION_DEAL, 'type': ORDER_TYPE_{direction}, 'volume': {lot}, 'price': {entry}, 'sl': {sl}, 'tp': {tp2}, 'magic': {self.magic_number}}})",
                "detail": f"ยิงคำสั่งเข้าโบรกเกอร์สำเร็จ! ได้รับ Ticket #84920188 (retcode=10009 TRADE_RETCODE_DONE)",
                "status": "EXECUTED 🚀"
            },
            {
                "step": 6,
                "phase": "LIVE TICK MONITOR & TP1 PARTIAL CLOSE",
                "code": f"if tick.price {'<=' if direction=='SELL' else '>='} {tp1}: mt5.Close(ticket=84920188, volume={round(lot*0.5, 2)})",
                "detail": f"ราคาวิ่งแตะเป้าหมาย TP1 (${tp1:,.2f}) -> บอทแบ่งปิดทำกำไรครึ่งแรก ล็อกเงินสด +${profit_tp1_half:,.2f} เข้าพอร์ตทันที!",
                "status": "TP1 LOCKED 💰"
            },
            {
                "step": 7,
                "phase": "AUTO BREAK-EVEN (TRADE_ACTION_SLTP)",
                "code": f"mt5.order_send({{'action': TRADE_ACTION_SLTP, 'position': 84920188, 'sl': {entry}, 'tp': {tp2}}})",
                "detail": f"บอทส่งคำสั่งขยับ Stop Loss จาก ${sl:,.2f} มาบังหน้าทุนที่ ${entry:,.2f} อัตโนมัติ (กลายเป็นไม้ Risk-Free 100%!)",
                "status": "RISK-FREE 🛡️"
            },
            {
                "step": 8,
                "phase": "TP2 FULL TARGET & CENTRAL CORE FEEDBACK",
                "code": f"nexus.deposit_trade_outcome(ticket=84920188, net_profit={total_demo_profit}, exp_reward=+180)",
                "detail": f"ราคาวิ่งแตะ TP2 (${tp2:,.2f}) ปิดออเดอร์รับกำไรรวม +${total_demo_profit:,.2f} (+2.3R) และส่งข้อมูลกลับเข้าแกนกลางบริษัทเพื่อเพิ่ม EXP ให้ทีม AI!",
                "status": "COMPLETED 🏆"
            }
        ]

        return {
            "ticket_id": 84920188,
            "symbol": self.mt5_symbol,
            "direction": direction,
            "lot_size": lot,
            "entry_price": entry,
            "sl_price": sl,
            "tp1_price": tp1,
            "tp2_price": tp2,
            "spread_points": spread_pts,
            "demo_profit_dollar": total_demo_profit,
            "request_payload": self.build_mt5_order_request(direction, lot, entry, sl, tp2),
            "steps_telemetry": steps_log,
            "tick_series": tick_series
        }
