import streamlit as st
import math

# -----------------------------------------------------------
# 1. [로직] 낙찰수수료
# -----------------------------------------------------------
def get_auction_fee(price, route):
    if route == "셀프":
        if price <= 1000000: return 75000
        elif price <= 5000000: return 185000
        elif price <= 10000000: return 245000
        elif price <= 20000000: return 250000
        elif price <= 30000000: return 250000
        else: return 360000
    elif route == "제로":
        if price <= 1000000: return 140000
        elif price <= 5000000: return 300000
        elif price <= 10000000: return 365000
        elif price <= 15000000: return 365000
        elif price <= 30000000: return 395000
        elif price <= 40000000: return 475000
        else: return 505000
    else: return 0

# -----------------------------------------------------------
# 2. [로직] 매입등록비
# -----------------------------------------------------------
def get_reg_cost(bid_price, p_type):
    threshold = 28500001
    rate = 0.0105
    if p_type == "개인":
        if bid_price >= threshold: return int(bid_price * rate)
        else: return 0
    else:
        supply_price = bid_price / 1.1
        if supply_price >= threshold: return int(supply_price * rate)
        else: return 0

# -----------------------------------------------------------
# 3. 메인 앱
# -----------------------------------------------------------
def smart_purchase_calculator_v36_vat_v14():
    st.set_page_config(page_title="매입견적서 V36-VAT by 김희주", layout="wide")
    
    st.markdown("""
    <style>
        html, body, [class*="css"] { font-size: 16px; }
        @media (max-width: 600px) { html, body, [class*="css"] { font-size: 14px; } }
        h1 { font-size: clamp(1.5rem, 4vw, 2.5rem) !important; font-weight: 800 !important; }
        .big-price { font-size: clamp(1.6rem, 3.5vw, 2.2rem); font-weight: 900; color: #4dabf7; margin-bottom: 0px; }
        .real-income { font-size: clamp(1.4rem, 2.5vw, 1.8rem); font-weight: bold; }
        .margin-rate { font-size: clamp(2.0rem, 4vw, 2.5rem); font-weight: 900; color: #ff6b6b; }
        .input-check { font-size: 0.9rem; color: #2e7d32; font-weight: bold; margin-top: -10px; margin-bottom: 20px; }
        .section-header { font-size: 1.1rem; font-weight: bold; margin-bottom: 10px; border-left: 4px solid #4dabf7; padding-left: 10px; }
        .detail-table-container { width: 100%; max-width: 450px; margin: 0 auto; }
        .detail-table { width: 100%; border-collapse: collapse; font-size: clamp(0.9rem, 2.5vw, 1.1rem); }
        .detail-table td { padding: 6px 10px; border-bottom: 1px solid #555; }
        @media (prefers-color-scheme: light) { .detail-table td { border-bottom: 1px solid #ddd; } }
        .detail-label { font-weight: bold; opacity: 0.9; white-space: nowrap; }
        .detail-value { text-align: right; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    if 'cost_dent' not in st.session_state: st.session_state['cost_dent'] = 0
    if 'cost_wheel' not in st.session_state: st.session_state['cost_wheel'] = 0
    if 'cost_etc' not in st.session_state: st.session_state['cost_etc'] = 0

    def smart_unit_converter(key):
        val = st.session_state[key]
        if 0 < val <= 20000: st.session_state[key] = val * 10000

    st.title("매입견적서 V36-VAT by 김희주")

    col1, col2, col3 = st.columns([1.5, 1, 1])
    with col1:
        sales_input = st.number_input("판매 예정가 (단위: 만원)", value=3500, step=10, format="%d")
        sales_price = sales_input * 10000
        st.markdown(f"<div class='input-check'>확인: {sales_price:,} 원</div>", unsafe_allow_html=True)
    with col2:
        p_type = st.radio("매입유형", ["개인", "사업자"])
    with col3:
        p_route = st.selectbox("매입루트", ["셀프", "제로", "개인거래"])

    st.markdown("---")

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown("<div class='section-header'>상품화 비용 입력 (세전 입력)</div>", unsafe_allow_html=True)
        st.caption("※ 비용/입찰가 입력 팁: 17 입력시 → 170,000원 / 3500 입력시 → 3,500만원")
        
        COST_AD = 270000 
        COST_DEPOSIT = 60000 # 비과세
        COST_POLISH_VAT = int(120000 * 1.1)

        raw_check = st.radio("성능점검비 (VAT포함 기준)", [44000, 66000], horizontal=True)
        # 교통비 비과세 반영
        cost_transport = st.selectbox("교통비 (비과세)", [30000, 50000, 80000, 130000, 170000, 200000])
        
        in_dent = st.number_input("판금/도색 (공급가)", step=10000, format="%d", key='cost_dent', on_change=smart_unit_converter, args=('cost_dent',))
        in_wheel = st.number_input("휠/타이어 (공급가)", step=10000, format="%d", key='cost_wheel', on_change=smart_unit_converter, args=('cost_wheel',))
        in_etc = st.number_input("기타비용 (공급가)", step=10000, format="%d", key='cost_etc', on_change=smart_unit_converter, args=('cost_etc',))

        cost_dent_vat = int(in_dent * 1.1)
        cost_wheel_vat = int(in_wheel * 1.1)
        cost_etc_vat = int(in_etc * 1.1)

        # 총 상품화 지출 (교통비와 입금비는 1.1 곱하지 않음)
        total_prep_vat = cost_transport + cost_dent_vat + cost_wheel_vat + cost_etc_vat + raw_check + COST_AD + COST_POLISH_VAT + COST_DEPOSIT
        st.caption(f"※ 광고(27만), 광택(13.2만), 입금(6만, 비과세), 교통비(비과세) 포함")

    budget_after_margin = int(sales_price * 0.955) # 4.5% 마진
    guide_bid = 0
    start_point = budget_after_margin - total_prep_vat
    
    for bid in range(start_point, start_point - 5000000, -10000):
        fee = get_auction_fee(bid, p_route)
        reg = get_reg_cost(bid, p_type)
        interest = int(bid * 0.01) # V36 금리 1%
        if (bid + total_prep_vat + fee + reg + interest) <= budget_after_margin:
            guide_bid = bid
            break
            
    if guide_bid > 0: guide_bid = math.ceil(guide_bid / 10000) * 10000

    if 'prev_guide_bid' not in st.session_state: st.session_state['prev_guide_bid'] = -1
    if guide_bid != st.session_state['prev_guide_bid']:
        st.session_state['my_bid_input'] = guide_bid
        st.session_state['prev_guide_bid'] = guide_bid

    with right_col:
        st.markdown("<div class='section-header'>입찰 금액 결정</div>", unsafe_allow_html=True)
        st.markdown("**적정 매입가 (Guide)**")
        st.markdown(f"<div class='big-price'>{guide_bid:,} 원</div>", unsafe_allow_html=True)
        st.write("")
        my_bid = st.number_input("입찰가 입력", step=10000, format="%d", label_visibility="collapsed", key='my_bid_input', on_change=smart_unit_converter, args=('my_bid_input',))

    st.markdown("---")

    res_fee = get_auction_fee(my_bid, p_route)
    res_reg = get_reg_cost(my_bid, p_type)
    res_interest = int(my_bid * 0.01)
    
    gross_margin = sales_price - my_bid - (raw_check + COST_AD + res_fee)
    dealer_income = int(gross_margin / 1.1)
    tax_base = dealer_income - res_reg
    tax_33 = int(tax_base * 0.033) if tax_base > 0 else 0
    
    real_income = dealer_income - (cost_transport + cost_dent_vat + cost_wheel_vat + cost_etc_vat + COST_POLISH_VAT + COST_DEPOSIT + res_reg + res_interest + tax_33)
    real_margin_rate = (real_income / my_bid * 100) if my_bid > 0 else 0
    total_cost = my_bid + total_prep_vat + res_reg + res_interest

    c_final1, c_final2 = st.columns(2)
    with c_final1:
        st.markdown("<div style='text-align:center;'>예상 실소득액 (세후)</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;' class='real-income'>{real_income:,} 원</div>", unsafe_allow_html=True)
    with c_final2:
        st.markdown("<div style='text-align:center;'>예상 이익률 (매입가 대비)</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;' class='margin-rate'>{real_margin_rate:.2f} %</div>", unsafe_allow_html=True)

    with st.expander("🧾 상세 견적 및 복사 (펼치기)", expanded=True):
        d_col1, d_col2 = st.columns([1, 1], gap="medium")
        with d_col1:
            st.caption("▼ 상세 내역 (확인용)")
            st.markdown(f"""
            <div class='detail-table-container'>
                <table class='detail-table'>
                    <tr><td class='detail-label'>판매가</td><td class='detail-value'>{sales_price:,} 원</td></tr>
                    <tr><td class='detail-label'>매입가</td><td class='detail-value' style='color:#4dabf7;'>{my_bid:,} 원</td></tr>
                    <tr><td class='detail-label'>총 소요원가</td><td class='detail-value' style='color:#aaa;'>{total_cost:,} 원</td></tr>
                    <tr><td colspan='2' style='height:8px; border-bottom:1px dashed #777;'></td></tr>
                    <tr><td class='detail-label'>예상이익률</td><td class='detail-value' style='color:#ff6b6b;'>{real_margin_rate:.2f} %</td></tr>
                    <tr><td class='detail-label'>실소득액</td><td class='detail-value'>{real_income:,} 원</td></tr>
                    <tr><td colspan='2' style='height:8px; border-bottom:1px dashed #777;'></td></tr>
                    <tr><td class='detail-label'>교통비(비과세)</td><td class='detail-value'>{cost_transport:,} 원</td></tr>
                    <tr><td class='detail-label'>판금/도색(VAT포함)</td><td class='detail-value'>{cost_dent_vat:,} 원</td></tr>
                    <tr><td class='detail-label'>휠/타이어(VAT포함)</td><td class='detail-value'>{cost_wheel_vat:,} 원</td></tr>
                    <tr><td class='detail-label'>기타비용(VAT포함)</td><td class='detail-value'>{cost_etc_vat:,} 원</td></tr>
                    <tr><td class='detail-label'>매입등록비</td><td class='detail-value'>{res_reg:,} 원</td></tr>
                    <tr><td class='detail-label'>낙찰수수료</td><td class='detail-value'>{res_fee:,} 원</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
        with d_col2:
            st.caption("▼ 복사 전용 텍스트 (금융이자 제외)")
            copy_text = f"""판매가   : {sales_price:,} 원
매입가   : {my_bid:,} 원
예상이익률 : {real_margin_rate:.2f} %
실소득액  : {real_income:,} 원
-------------------------
교통비    : {cost_transport:,} 원
판금/도색  : {cost_dent_vat:,} 원
휠/타이어  : {cost_wheel_vat:,} 원
기타비용   : {cost_etc_vat:,} 원
매입등록비 : {res_reg:,} 원
낙찰수수료 : {res_fee:,} 원"""
            st.code(copy_text, language="text")

if __name__ == "__main__":
    smart_purchase_calculator_v36_vat_v14()
