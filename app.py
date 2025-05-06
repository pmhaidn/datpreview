import streamlit as st
import pandas as pd
import re
from datetime import datetime
import base64

# Thiết lập trang
st.set_page_config(
    page_title="DAT File Parser",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Thêm CSS tùy chỉnh
def add_custom_css():
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    
    h1, h2, h3 {
        color: #1E88E5;
    }
    
    h1 {
        font-size: 1.8rem;
        margin-bottom: 1rem;
    }
    
    h2 {
        font-size: 1.5rem;
        margin-bottom: 0.8rem;
    }
    
    h3 {
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 5px 5px 0px 0px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5;
        color: white;
    }
    
    .stDataFrame {
        border: 1px solid #E0E0E0;
        border-radius: 5px;
    }
    
    .download-btn {
        background-color: #4CAF50;
        color: white;
        padding: 10px 15px;
        border: none;
        border-radius: 5px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
    }
    
    .mini-statistic-box {
        background-color: #f8f9fa;
        border-radius: 4px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #1E88E5;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .mini-statistic-box p {
        margin: 0;
        font-weight: bold;
    }
    
    .data-preview {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        height: 120px;
        overflow-y: auto;
        font-family: monospace;
        font-size: 0.8rem;
        border: 1px solid #ddd;
    }
    
    .upload-container {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .preview-container {
        background-color: white;
        padding: 0.8rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .preview-title {
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
        color: #424242;
    }
    
    .compact-table {
        font-size: 0.85rem;
    }
    
    .stExpander {
        border: 1px solid #eee;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    
    /* Định dạng nút download */
    .download-area {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-top: 1rem;
    }
    
    /* Định dạng tabs */
    .data-tabs {
        margin-top: 1rem;
    }
    
    /* Ẩn selectbox label */
    div[data-testid="stSelectbox"] > div:first-child {
        display: none;
    }
    
    /* Tùy chỉnh màu sắc cho selectbox */
    div[data-testid="stSelectbox"] {
        max-width: 300px;
    }
    
    div[data-testid="stDownloadButton"] {
        margin: 0 auto;
        display: block;
    }
    
    div[data-testid="stDownloadButton"] button {
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        font-weight: 500;
        border-radius: 5px;
        border: none;
        transition: all 0.3s ease;
    }
    
    div[data-testid="stDownloadButton"] button:hover {
        background-color: #45a049;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# Định nghĩa mapping cho các trường (chỉ giữ tiếng Việt)
FIELD_MAPPINGS = {
    'HR': 'Bản ghi tiêu đề',
    'REV': 'Phiên bản',
    'DATE': 'Ngày tạo file',
    'DR': 'Bản ghi chi tiết',
    'MTI': 'Loại tin nhắn',
    'F2': 'Số tài khoản chính',
    'F3': 'Mã xử lý',
    'SVC': 'Mã dịch vụ',
    'TCC': 'Mã loại giao dịch',
    'F4': 'Số tiền giao dịch',
    'RTA': 'Số tiền đối soát',
    'F49': 'Mã tiền tệ giao dịch',
    'F5': 'Số tiền đối soát',
    'F50': 'Mã tiền tệ đối soát',
    'F9': 'Tỷ giá chuyển đổi',
    'F6': 'Số tiền thanh toán',
    'RCA': 'Số tiền đối soát thanh toán',
    'F51': 'Mã tiền tệ thanh toán',
    'F10': 'Tỷ giá chuyển đổi thanh toán',
    'F11': 'Số kiểm tra hệ thống',
    'F12': 'Thời gian giao dịch',
    'F13': 'Ngày giao dịch',
    'F15': 'Ngày thanh toán',
    'F18': 'Loại merchant',
    'F22': 'Phương thức nhập liệu',
    'F25': 'Mã điều kiện POS',
    'F41': 'ID thiết bị chấp nhận thẻ',
    'ACQ': 'Tổ chức phát hành',
    'ISS': 'Tổ chức phát hành',
    'MID': 'Mã merchant',
    'BNB': 'Tổ chức thụ hưởng',
    'F102': 'Định danh tài khoản 1',
    'F103': 'Định danh tài khoản 2',
    'SVFISSNP': 'Phí dịch vụ phát hành không xử lý',
    'IRFISSACQ': 'Phí giao dịch phát hành',
    'IRFISSBNB': 'Phí giao dịch phát hành thụ hưởng',
    'SVFACQNP': 'Phí dịch vụ phát hành không xử lý',
    'IRFACQISS': 'Phí giao dịch phát hành',
    'IRFACQBNB': 'Phí giao dịch phát hành thụ hưởng',
    'SVFBNBNP': 'Phí dịch vụ thụ hưởng không xử lý',
    'IRFBNBISS': 'Phí giao dịch thụ hưởng phát hành',
    'IRFBNBACQ': 'Phí giao dịch thụ hưởng phát hành',
    'F37': 'Số tham chiếu truy xuất',
    'F38': 'ID phản hồi xác thực',
    'TRN': 'Số tham chiếu giao dịch',
    'RRC': 'Mã lý do phản hồi',
    'RSV1': 'Trường dự phòng 1',
    'RSV2': 'Trường dự phòng 2',
    'RSV3': 'Trường dự phòng 3',
    'CSR': 'Mã kiểm tra',
    'TR': 'Bản ghi tổng kết',
    'NOT': 'Số lượng giao dịch',
    'CRE': 'Người tạo',
    'TIME': 'Thời gian',
    'CSF': 'Mã kiểm tra file'
}

def parse_dat_file(content):
    lines = content.strip().split('\n')
    records = []
    
    for line in lines:
        if line.startswith('HR'):
            record_type = 'Header'
        elif line.startswith('DR'):
            record_type = 'Detail'
        elif line.startswith('TR'):
            record_type = 'Trailer'
        else:
            continue
            
        # Tách các trường bằng regex
        fields = re.findall(r'\[(.*?)\](.*?)(?=\[|$)', line)
        record = {'Loại bản ghi': record_type}
        
        for field_name, field_value in fields:
            if field_name in FIELD_MAPPINGS:
                record[FIELD_MAPPINGS[field_name]] = field_value.strip()
            else:
                record[field_name] = field_value.strip()
                
        records.append(record)
    
    return pd.DataFrame(records)

def filter_non_empty_columns(df):
    # Lọc các cột có ít nhất một giá trị không phải NaN
    return df.loc[:, df.notna().any()]

def get_download_link(df, filename="dat_analysis.csv", text="Tải xuống CSV"):
    """Tạo link download cho dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="download-btn">{text}</a>'
    return href

def display_mini_stats(title, value, icon="📊"):
    """Hiển thị thống kê nhỏ gọn"""
    st.markdown(f"""
    <div class="mini-statistic-box">
        <span>{icon} {title}</span>
        <p>{value}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Thêm CSS tùy chỉnh
    add_custom_css()
    
    # Sidebar
    with st.sidebar:
        st.title("DAT File Parser")
        st.markdown("---")
        st.markdown("### Hướng dẫn sử dụng")
        st.markdown("""
        1. Tải lên file DAT của bạn
        2. Xem dữ liệu được phân tích tự động
        3. Tải xuống kết quả phân tích dưới dạng CSV
        """)
        st.markdown("---")
        st.markdown("### Thông tin")
        st.markdown("Ứng dụng phân tích file DAT với định dạng tiêu chuẩn.")
        
    # Main layout
    st.title("📊 Phân tích File DAT")
    
    # Khu vực upload file trong container đẹp hơn
    st.markdown('<div class="upload-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 3])
    
    with col1:
        uploaded_file = st.file_uploader("Chọn file DAT", type=['dat'])
    
    with col2:
        st.markdown('<div class="preview-title">Dữ liệu gốc file DAT</div>', unsafe_allow_html=True)
        if uploaded_file is not None:
            content = uploaded_file.getvalue().decode('utf-8')
            st.markdown(f'<div class="data-preview">{content}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="data-preview">Chưa có dữ liệu, vui lòng tải file lên.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Hiển thị bảng định nghĩa gọn gàng ở phía dưới upload
    if uploaded_file is not None:
        with st.expander("Xem bảng định nghĩa các trường", expanded=False):
            mapping_df = pd.DataFrame([
                {'Mã trường': k, 'Định nghĩa': v}
                for k, v in FIELD_MAPPINGS.items()
            ])
            st.dataframe(mapping_df, height=250, use_container_width=True, hide_index=True)
    
    # Xử lý file đã upload
    if uploaded_file is not None:
        with st.spinner("Đang phân tích dữ liệu..."):
            if 'content' not in locals():
                content = uploaded_file.getvalue().decode('utf-8')
            df = parse_dat_file(content)
            
            # Tách dữ liệu theo loại bản ghi
            header_df = df[df['Loại bản ghi'] == 'Header'].copy()
            detail_df = df[df['Loại bản ghi'] == 'Detail'].copy()
            trailer_df = df[df['Loại bản ghi'] == 'Trailer'].copy()
            
            # Lọc các cột có giá trị cho từng loại bản ghi
            header_df = filter_non_empty_columns(header_df)
            detail_df = filter_non_empty_columns(detail_df)
            trailer_df = filter_non_empty_columns(trailer_df)
        
        st.success("Phân tích hoàn tất!")
        
        # Hiển thị thông tin tổng quan trong expander nhỏ gọn
        with st.expander("📈 Thông tin tổng quan", expanded=False):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                display_mini_stats("Tổng bản ghi", len(df), "📝")
            with col2:
                display_mini_stats("Bản ghi tiêu đề", len(header_df), "🔼")
            with col3:
                display_mini_stats("Bản ghi chi tiết", len(detail_df), "📄")
            with col4:
                display_mini_stats("Bản ghi tổng kết", len(trailer_df), "🔽")
        
        # Tạo tabs để phân loại nội dung (đã Việt hóa)
        st.markdown('<div class="data-tabs">', unsafe_allow_html=True)
        tab1, tab2, tab3 = st.tabs(["🔼 Bản ghi tiêu đề", "📄 Bản ghi chi tiết", "🔽 Bản ghi tổng kết"])
        
        with tab1:
            if not header_df.empty:
                st.dataframe(header_df, use_container_width=True, hide_index=True)
            else:
                st.info("Không có bản ghi tiêu đề nào trong file này.")
        
        with tab2:
            if not detail_df.empty:
                st.dataframe(detail_df, use_container_width=True, hide_index=True)
            else:
                st.info("Không có bản ghi chi tiết nào trong file này.")
        
        with tab3:
            if not trailer_df.empty:
                st.dataframe(trailer_df, use_container_width=True, hide_index=True)
            else:
                st.info("Không có bản ghi tổng kết nào trong file này.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tạo nút download CSV (một nút duy nhất với menu)
        st.markdown('<div class="download-area">', unsafe_allow_html=True)
        st.markdown("### 💾 Tải xuống dữ liệu")
        
        # Chuẩn bị dữ liệu CSV
        csv_all = df.to_csv(index=False)
        csv_header = header_df.to_csv(index=False)
        csv_detail = detail_df.to_csv(index=False)
        csv_trailer = trailer_df.to_csv(index=False)
        
        # Chọn loại dữ liệu để tải xuống
        download_type = st.selectbox(
            "Chọn loại dữ liệu:",
            ["Tất cả bản ghi", "Bản ghi tiêu đề", "Bản ghi chi tiết", "Bản ghi tổng kết"]
        )
        
        # Sử dụng download_type để quyết định data nào sẽ được tải xuống
        if download_type == "Tất cả bản ghi":
            file_data = csv_all
            file_name = 'dat_analysis_all.csv'
        elif download_type == "Bản ghi tiêu đề":
            file_data = csv_header
            file_name = 'dat_header.csv'
        elif download_type == "Bản ghi chi tiết":
            file_data = csv_detail
            file_name = 'dat_detail.csv'
        else:  # Bản ghi tổng kết
            file_data = csv_trailer
            file_name = 'dat_trailer.csv'
        
        # Tạo nút download
        st.markdown('<div class="custom-download-btn">', unsafe_allow_html=True)
        st.download_button(
            label=f"📥 Tải xuống CSV",
            data=file_data,
            file_name=file_name,
            mime='text/csv',
        )
        st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        # Hiển thị hộp thông tin khi chưa có file
        st.info("👆 Vui lòng tải lên file DAT để bắt đầu phân tích.")
        
        # Hiển thị ví dụ định dạng
        with st.expander("🔍 Xem ví dụ định dạng file DAT"):
            st.code("""HR[REV]  971003[DATE]28042025
DR[MTI]0210[F2]   9704030619620215[F3]910000[SVC]    IF_DEP[TCC]97[F4]000010000000[RTA]000010000000[F49]704[F5]000010000000[F50]704[F9]00000001[F6]000000000000[RCA]000000000000[F51]704[F10]00000000[F11]304956[F12]103105[F13]0428[F15]0428[F18]6011[F22]000[F25]00[F41]00000001[ACQ]  971003[ISS]  971003[MID]               [BNB]  970403[F102]            9704030619620215[F103]            9704030237940215[SVFISSNP]000000038500[IRFISSACQ]000000000000[IRFISSBNB]000000033000[SVFACQNP]000000000000[IRFACQISS]000000000000[IRFACQBNB]000000000000[SVFBNBNP]000000000000[IRFBNBISS]000000000000[IRFBNBACQ]000000000000[F37]745811065932[F38]747210[TRN]5118IBT1aQGDB517[RRC]0000[RSV1]                                                                                                    [RSV2]                                                                                                    [RSV3]                                                                                                    [CSR]aa02e5507e8ca45c674196f8b428afef
TR[NOT]000000001[CRE]               hoind[TIME]041507[DATE]29042025[CSF]1af6c580d04185ee04f5c0811f503b5c""")

# Chạy ứng dụng
if __name__ == '__main__':
    main() 