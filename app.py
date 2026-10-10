import streamlit as st
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="Mini ERP System", page_icon="📊", layout="wide")

# تهيئة قاعدة البيانات المؤقتة داخل الذاكرة لو مش موجودة
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=["المنتج", "الكمية", "السعر"])

if 'sales' not in st.session_state:
    st.session_state.sales = pd.DataFrame(columns=["المنتج", "الكمية المباعة", "الإجمالي", "الوقت"])

# عنوان التطبيق
st.title("🚀 نظام تخطيط موارد المؤسسات المصغر (Mini-ERP)")
st.write("نظام مبسط يربط بين إدارة المخزون، المشتريات، المبيعات، والحسابات لشركات االنشأة.")

# القائمة الجانبية للتنقل بين الأقسام
menu = st.sidebar.selectbox("اختر القسم", ["إدارة المخزون (Inventory)", "المشتريات (Purchasing)", "المبيعات (Sales & POS)", "التقارير المالية (Finance)"])

# 1. قسم المخزون
if menu == "إدارة المخزون (Inventory)":
    st.header("📦 إدارة المخزون والمنتجات")
    
    # نموذج إضافة منتج جديد
    with st.form("add_product"):
        p_name = st.text_input("اسم المنتج")
        p_qty = st.number_input("الكمية الأولية", min_value=0, step=1)
        p_price = st.number_input("سعر البيع", min_value=0.0, step=0.5)
        submit = st.form_submit_button("إضافة للمخزن")
        
        if submit and p_name:
            new_row = pd.DataFrame({"المنتج": [p_name], "الكمية": [p_qty], "السعر": [p_price]})
            st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
            st.success(f"تم إضافة المنتج '{p_name}' بنجاح!")

    st.subheader("المنتجات الحالية في المخزن:")
    st.dataframe(st.session_state.inventory, use_container_width=True)

# 2. قسم المشتريات
elif menu == "المشتريات (Purchasing)":
    st.header("🛒 إدارة المشتريات وتوريد البضائع")
    if st.session_state.inventory.empty:
        st.warning("برجاء إضافة منتجات في المخزن أولاً.")
    else:
        with st.form("purchase_form"):
            selected_product = st.selectbox("اختر المنتج لزيادة كميته", st.session_state.inventory["المنتج"])
            added_qty = st.number_input("الكمية المشتراة للمخزن", min_value=1, step=1)
            p_submit = st.form_submit_button("تحديث المخزون (شراء)")
            
            if p_submit:
                idx = st.session_state.inventory[st.session_state.inventory["المنتج"] == selected_product].index[0]
                st.session_state.inventory.loc[idx, "الكمية"] += added_qty
                st.success(f"تم توريد {added_qty} قطعة جديدة من {selected_product} وزيادة المخزن بنجاح!")
                st.dataframe(st.session_state.inventory, use_container_width=True)

# 3. قسم المبيعات
elif menu == "المبيعات (Sales & POS)":
    st.header("💰 نقطة البيع والمبيعات (POS)")
    if st.session_state.inventory.empty:
        st.warning("لا توجد منتجات متاح بيعها.")
    else:
        with st.form("sales_form"):
            s_product = st.selectbox("اختر المنتج للبيع", st.session_state.inventory["المنتج"])
            s_qty = st.number_input("الكمية المطلوبة للبيع", min_value=1, step=1)
            s_submit = st.form_submit_button("إتمام عملية البيع")
            
            if s_submit:
                current_qty = int(st.session_state.inventory.loc[st.session_state.inventory["المنتج"] == s_product, " الكمية" if " الكمية" in st.session_state.inventory.columns else "الكمية"].values[0])
                
                if s_qty > current_qty:
                    st.error("الكمية المطلوبة غير متوفرة في المخزن!")
                else:
                    # خصم الكمية من المخزن
                    idx = st.session_state.inventory[st.session_state.inventory["المنتج"] == s_product].index[0]
                    price = st.session_state.inventory.loc[idx, "السعر"]
                    st.session_state.inventory.loc[idx, "الكمية"] -= s_qty
                    
                    # تسجيل المبيعات
                    total_price = s_qty * price
                    sale_row = pd.DataFrame({"المنتج": [s_product], "الكمية المباعة": [s_qty], "الإجمالي": [total_price], "الوقت": [pd.Timestamp.now()]})
                    st.session_state.sales = pd.concat([st.session_state.sales, sale_row], ignore_index=True)
                    
                    st.success(f"تم البيع بنجاح! الإجمالي المستحق: {total_price} جنيه")

        st.subheader("سجل الفواتير والمبيعات:")
        st.dataframe(st.session_state.sales, use_container_width=True)

# 4. التقارير المالية
elif menu == "التقارير المالية (Finance)":
    st.header("📈 تقارير الأرباح والحسابات")
    if not st.session_state.sales.empty:
        total_revenue = st.session_state.sales["الإجمالي"].sum()
        st.metric(label="إجمالي المبيعات (الإيرادات)", value=f"{total_revenue} جنيه")
    else:
        st.info("لم يتم تسجيل أي مبيعات حتى الآن لعرض التقارير.")