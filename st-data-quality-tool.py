import streamlit as st
import pandas as pd
import numpy as np

# --- 1. 앱 제목 ---
st.title("📊 데이터 품질 점검 도구")

st.markdown("""
이 도구는 데이터 품질을 점검하기 위해 설계되었습니다.
업로드한 데이터에 대해 다음 항목을 점검합니다:
- **고유성**(Uniqueness): 중복된 값이 없는지
- **완전성**(Completeness): 결측치가 없는지
- **유효성**(Validity): 데이터가 유효한 범위 내에 있는지
""")

# --- 2. 파일 업로드 또는 샘플 데이터 ---
st.header("📥 데이터 업로드")
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

# 샘플 데이터 생성 옵션
use_sample_data = st.checkbox("샘플 데이터 사용하기")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("데이터가 성공적으로 업로드되었습니다!")
    st.dataframe(df, use_container_width=True)
elif use_sample_data:
    # 샘플 데이터 생성
    data = {
        'user_id': [1001, 1002, 1003, 1004, 1003, 1005],  # 1003 중복
        'user_name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank'],
        'order_count': [5, 12, np.nan, 8, 3, 15],  # 1003의 order_count는 결측치(NaN)
        'join_year': [2022, 2021, 2023, 2025, 2024, 2023] # 2025는 미래 데이터 (유효성 오류)
    }
    df = pd.DataFrame(data)
    st.info("샘플 데이터를 사용합니다.")
    st.dataframe(df, use_container_width=True)
else:
    st.info("CSV 파일을 업로드하거나 샘플 데이터를 사용하세요.")
    st.stop()

# --- 3. 데이터 품질 점검 항목 설정 ---
st.header("🔍 품질 점검 설정")

# 고유성 점검 컬럼 선택
unique_col = st.selectbox("고유성(Uniqueness) 점검할 컬럼을 선택하세요", options=df.columns.tolist(), index=0)
# 필수값 점검 컬럼 선택
complete_col = st.selectbox("필수값(Completeness) 점검할 컬럼을 선택하세요", options=df.columns.tolist(), index=2)
# 유효성 점검 컬럼 및 설정
numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
valid_col = st.selectbox("유효성(Validity) 점검할 컬럼을 선택하세요", options=numeric_cols, index=min(2, len(numeric_cols)-1) if len(numeric_cols) > 0 else 0)
valid_max_value = st.number_input(f"{valid_col}의 최대 허용값을 입력하세요", value=2024)

# 점검 실행 버튼
if st.button("데이터 품질 점검 실행", type="primary"):
    # 품질 점검 결과를 저장할 리스트
    dq_results = []

    def run_dq_check(check_name, status, message):
        """점검 결과를 리스트에 추가하는 헬퍼 함수"""
        dq_results.append({
            '점검 항목': check_name,
            '상태': '❌ 오류' if status == 'FAIL' else '✅ 정상',
            '메시지': message
        })

    # --- 4. 데이터 품질 점검 실행 ---

    # 1. 고유성(Uniqueness) 점검
    col = unique_col
    is_unique = df[col].is_unique
    if not is_unique:
        duplicate_count = df[col].duplicated(keep='first').sum()
        run_dq_check(
            check_name=f'{col} 고유성 점검',
            status='FAIL',
            message=f'중복된 값 {duplicate_count}건 발견. (오류율: {duplicate_count / len(df) * 100:.2f}%)'
        )
    else:
        run_dq_check(check_name=f'{col} 고유성 점검', status='PASS', message='고유성 확보.')

    # 2. 필수값(Completeness) 점검
    col = complete_col
    null_count = df[col].isnull().sum()
    if null_count > 0:
        run_dq_check(
            check_name=f'{col} 필수값 점검',
            status='FAIL',
            message=f'결측치(NULL) {null_count}건 발견. (오류율: {null_count / len(df) * 100:.2f}%)'
        )
    else:
        run_dq_check(check_name=f'{col} 필수값 점검', status='PASS', message='결측치 없음.')

    # 3. 유효성(Validity) 점검
    col = valid_col
    current_year = valid_max_value
    invalid_data = df[df[col] > current_year]
    if not invalid_data.empty:
        invalid_count = len(invalid_data)
        run_dq_check(
            check_name=f'{col} 유효성 점검',
            status='FAIL',
            message=f'유효 범위 초과 데이터 {invalid_count}건 발견 (최대값 {current_year} 초과). ({invalid_data[col].to_list()})'
        )
    else:
        run_dq_check(check_name=f'{col} 유효성 점검', status='PASS', message='유효한 범위 내 데이터.')

    # --- 5. 결과 표시 ---
    st.header("📋 데이터 품질 점검 결과")

    # 결과를 DataFrame으로 변환
    results_df = pd.DataFrame(dq_results)

    # 상태에 따라 색상 구분
    def color_status(val):
        color = 'red' if '❌' in val else 'green'
        return f'background-color: {color}; color: white; font-weight: bold'

    # 결과 표시
    st.dataframe(
        results_df.style.applymap(color_status, subset=['상태']),
        use_container_width=True
    )

    # 요약 통계
    total_checks = len(results_df)
    error_checks = len(results_df[results_df['상태'].str.contains('❌')])
    pass_checks = total_checks - error_checks

    col1, col2, col3 = st.columns(3)
    col1.metric("총 점검 항목", total_checks)
    col2.metric("정상 항목", pass_checks)
    col3.metric("오류 항목", error_checks)

    # --- 6. 오류 데이터 상세 조회 ---
    st.header("🔍 오류 데이터 상세 조회")

    # 고유성 오류 데이터
    if any('고유성' in str(row['점검 항목']) and '❌' in str(row['상태']) for _, row in results_df.iterrows()):
        st.subheader(f"❌ 중복된 {unique_col} 데이터")
        duplicate_ids = df[df[unique_col].duplicated(keep=False)][unique_col].tolist()
        if duplicate_ids:
            st.dataframe(df[df[unique_col].isin(duplicate_ids)].sort_values(by=unique_col), use_container_width=True)

    # 필수값 오류 데이터
    if any('필수값' in str(row['점검 항목']) and '❌' in str(row['상태']) for _, row in results_df.iterrows()):
        st.subheader(f"❌ 결측치가 있는 {complete_col} 데이터")
        null_rows = df[df[complete_col].isnull()]
        if not null_rows.empty:
            st.dataframe(null_rows, use_container_width=True)

    # 유효성 오류 데이터
    if any('유효성' in str(row['점검 항목']) and '❌' in str(row['상태']) for _, row in results_df.iterrows()):
        st.subheader(f"❌ 유효 범위를 벗어난 {valid_col} 데이터")
        invalid_rows = df[df[valid_col] > valid_max_value]
        if not invalid_rows.empty:
            st.dataframe(invalid_rows, use_container_width=True)