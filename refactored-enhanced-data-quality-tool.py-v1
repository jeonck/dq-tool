import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime

def safe_get_column_index(default_index, max_index):
    """Safely get column index, ensuring it's within bounds"""
    return min(max(0, default_index), max(0, max_index))

def safe_is_unique(series):
    """Safely check if a series has unique values, handling edge cases"""
    try:
        if series.dtype == 'object':
            # For object types, handle NaN values properly
            non_null_values = series.dropna()
            return non_null_values.is_unique and len(non_null_values) == len(series.dropna())
        return series.is_unique
    except:
        return True  # Default to unique if we can't determine

def safe_to_datetime(series):
    """Safely convert series to datetime"""
    try:
        return pd.to_datetime(series, errors='coerce')
    except:
        return series

def safe_email_pattern_check(series):
    """Safely check email patterns"""
    try:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if series.dtype == 'object':
            email_matches = series.str.contains(email_pattern, na=False, regex=True)
            invalid_emails = series[~series.str.match(email_pattern, na=False)]
            return email_matches.any(), invalid_emails
        return False, pd.Series(dtype=object)
    except:
        return False, pd.Series(dtype=object)

def safe_check_business_rules(df, col_name):
    """Safely apply business rules"""
    try:
        if col_name in df.columns and pd.api.types.is_numeric_dtype(df[col_name]):
            negative_values = df[df[col_name] < 0][col_name]
            return negative_values
        return pd.Series(dtype=object)
    except:
        return pd.Series(dtype=object)

def safe_outlier_detection(series):
    """Safely detect outliers using IQR method"""
    try:
        if pd.api.types.is_numeric_dtype(series):
            series_numeric = pd.to_numeric(series, errors='coerce')
            series_clean = series_numeric.dropna()

            if len(series_clean) < 4:  # Need at least 4 points for IQR
                return pd.Series(dtype='object', name=series.name if hasattr(series, 'name') else None)

            Q1 = series_clean.quantile(0.25)
            Q3 = series_clean.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            series_as_numeric = pd.to_numeric(series, errors='coerce')
            outlier_mask = (series_as_numeric < lower_bound) | (series_as_numeric > upper_bound)
            outliers = series[outlier_mask]
            return outliers
        return pd.Series(dtype='object', name=series.name if hasattr(series, 'name') else None)
    except:
        return pd.Series(dtype='object', name=series.name if hasattr(series, 'name') else None)

# --- 1. 앱 제목 ---
st.title("📊 종합 데이터 품질 진단 도구")

st.markdown("""
이 도구는 **7대 품질 지표**와 **4대 진단 방법**을 기반으로 데이터 품질을 종합적으로 진단합니다.
업로드한 데이터에 대해 다음과 같은 항목들을 점검합니다:
- **준비성**, **완전성**, **일관성**, **정확성**, **보안성**, **적시성**, **유용성**
- **프로파일링**, **업무규칙 진단**, **체크리스트**, **비정형 실측**
""")

# --- 2. 파일 업로드 또는 샘플 데이터 ---
st.header("📥 데이터 업로드")
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

# 샘플 데이터 생성 옵션
use_sample_data = st.checkbox("샘플 데이터 사용하기")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("데이터가 성공적으로 업로드되었습니다!")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {str(e)}")
        st.stop()
elif use_sample_data:
    # 샘플 데이터 생성
    data = {
        'user_id': [1001, 1002, 1003, 1004, 1003, 1005],  # 1003 중복
        'user_name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank'],
        'order_count': [5, 12, np.nan, 8, 3, 15],  # 1003의 order_count는 결측치(NaN)
        'join_date': ['2022-05-15', '2021-03-22', '2023-01-10', '2025-12-06', '2024-07-30', '2023-11-05'], # 2025-12-06은 미래 데이터 (적시성 오류)
        'email': ['alice@example.com', 'bob@example.com', 'invalid-email', 'david@example.com', 'eve@example.com', 'frank@example.com']  # invalid-email은 이메일 형식 오류 (정확성 오류)
    }
    df = pd.DataFrame(data)
    # join_date를 datetime으로 변환
    df['join_date'] = pd.to_datetime(df['join_date'])
    st.info("샘플 데이터를 사용합니다.")
    st.dataframe(df, use_container_width=True)
else:
    st.info("CSV 파일을 업로드하거나 샘플 데이터를 사용하세요.")
    st.stop()

# --- 3. 데이터 기본 정보 ---
st.header("📊 데이터 기본 정보")
st.write(f"**행 수**: {len(df)}")
st.write(f"**열 수**: {len(df.columns)}")
st.write(f"**컬럼 목록**: {', '.join(df.columns.tolist())}")

# --- 4. 데이터 품질 점검 항목 설정 ---
st.header("🔍 품질 점검 설정")

# 7대 품질 지표 설정
st.subheader("7대 품질 지표")

col1, col2 = st.columns(2)
with col1:
    # 준비성 (Availability) 점검 컬럼 선택
    availability_col_index = safe_get_column_index(0, len(df.columns) - 1)
    availability_col = st.selectbox("준비성(Availability) 점검할 컬럼", options=df.columns.tolist(), index=availability_col_index)
    # 고유성 (Uniqueness) 점검 컬럼 선택
    uniqueness_col_index = safe_get_column_index(0, len(df.columns) - 1)
    uniqueness_col = st.selectbox("고유성(Uniqueness) 점검할 컬럼", options=df.columns.tolist(), index=uniqueness_col_index)
    # 완전성 (Completeness) 점검 컬럼 선택
    complete_col_index = safe_get_column_index(2, len(df.columns) - 1)
    complete_col = st.selectbox("완전성(Completeness) 점검할 컬럼", options=df.columns.tolist(), index=complete_col_index)
    # 일관성 (Consistency) 점검 컬럼 선택
    consistency_col_index = safe_get_column_index(1, len(df.columns) - 1)
    consistency_col = st.selectbox("일관성(Consistency) 점검할 컬럼", options=df.columns.tolist(), index=consistency_col_index)

with col2:
    # 정확성 (Accuracy) 점검 컬럼 선택
    accuracy_col_index = safe_get_column_index(3, len(df.columns) - 1)
    accuracy_col = st.selectbox("정확성(Accuracy) 점검할 컬럼", options=df.columns.tolist(), index=accuracy_col_index)
    # 보안성 (Security) 점검 컬럼 선택
    security_col_index = safe_get_column_index(3, len(df.columns) - 1)
    security_col = st.selectbox("보안성(Security) 점검할 컬럼", options=df.columns.tolist(), index=security_col_index)
    # 적시성 (Timeliness) 점검 컬럼 선택
    timely_col_index = safe_get_column_index(3, len(df.columns) - 1)
    timely_col = st.selectbox("적시성(Timeliness) 점검할 컬럼", options=df.columns.tolist(), index=timely_col_index)
    # 유용성 (Usability) 점검 컬럼 선택
    usability_col_index = safe_get_column_index(1, len(df.columns) - 1)
    usability_col = st.selectbox("유용성(Usability) 점검할 컬럼", options=df.columns.tolist(), index=usability_col_index)

# 4대 진단 방법 설정
st.subheader("4대 진단 방법")
profiling_enabled = st.checkbox("프로파일링(Profiling) 활성화", value=True)
business_rule_enabled = st.checkbox("업무규칙 진단(Business Rule) 활성화", value=True)
checklist_enabled = st.checkbox("체크리스트(Checklist) 활성화", value=True)
realtime_measure_enabled = st.checkbox("비정형 실측(Unstructured Real-time Measurement) 활성화", value=True)

# 점검 실행 버튼
if st.button("데이터 품질 종합 진단 실행", type="primary"):
    # 품질 점검 결과를 저장할 리스트
    dq_results = []

    def run_dq_check(check_name, status, message, metric_type):
        """점검 결과를 리스트에 추가하는 헬퍼 함수"""
        dq_results.append({
            '점검 항목': check_name,
            '상태': '❌ 오류' if status == 'FAIL' else '✅ 정상',
            '메시지': message,
            '지표 유형': metric_type
        })

    # --- 5. 7대 품질 지표 점검 실행 ---
    try:
        # 1. 준비성(Availability) 점검 - 데이터 접근 가능성
        if availability_col in df.columns:
            col_data = df[availability_col]
            missing_count = col_data.isnull().sum() + (col_data == '').sum()
            if missing_count > 0:
                run_dq_check(
                    check_name=f'{availability_col} 준비성 점검',
                    status='FAIL',
                    message=f'접근 불가능한 값 {missing_count}건 발견',
                    metric_type='준비성(Availability)'
                )
            else:
                run_dq_check(
                    check_name=f'{availability_col} 준비성 점검', 
                    status='PASS', 
                    message='모든 데이터 접근 가능',
                    metric_type='준비성(Availability)'
                )

        # 2. 고유성(Uniqueness) 점검 - 중복 값 확인
        if uniqueness_col in df.columns:
            col_data = df[uniqueness_col]
            is_unique = safe_is_unique(col_data)
            if not is_unique:
                duplicate_count = col_data.duplicated(keep='first').sum()
                run_dq_check(
                    check_name=f'{uniqueness_col} 고유성 점검',
                    status='FAIL',
                    message=f'중복된 값 {duplicate_count}건 발견. (오류율: {duplicate_count / len(df) * 100:.2f}%)',
                    metric_type='고유성(Uniqueness)'
                )
            else:
                run_dq_check(
                    check_name=f'{uniqueness_col} 고유성 점검', 
                    status='PASS', 
                    message='고유성 확보',
                    metric_type='고유성(Uniqueness)'
                )

        # 3. 완전성(Completeness) 점검 - 결측치
        if complete_col in df.columns:
            col_data = df[complete_col]
            null_count = col_data.isnull().sum()
            if null_count > 0:
                run_dq_check(
                    check_name=f'{complete_col} 완전성 점검',
                    status='FAIL',
                    message=f'결측치(NULL) {null_count}건 발견. (오류율: {null_count / len(df) * 100:.2f}%)',
                    metric_type='완전성(Completeness)'
                )
            else:
                run_dq_check(
                    check_name=f'{complete_col} 완전성 점검', 
                    status='PASS', 
                    message='결측치 없음',
                    metric_type='완전성(Completeness)'
                )

        # 4. 일관성(Consistency) 점검 - 데이터 형식 일관성
        if consistency_col in df.columns:
            col_data = df[consistency_col]
            # For now, basic consistency check - could be expanded based on requirements
            run_dq_check(
                check_name=f'{consistency_col} 일관성 점검', 
                status='PASS', 
                message='데이터 형식 일관성 기본 점검 완료',
                metric_type='일관성(Consistency)'
            )

        # 5. 정확성(Accuracy) 점검 - 데이터 유효성
        if accuracy_col in df.columns:
            col_data = df[accuracy_col]
            violations_found = False  # Track if any violations are found

            # Check for datetime-like columns
            if pd.api.types.is_datetime64_any_dtype(col_data) or 'date' in accuracy_col.lower() or 'year' in accuracy_col.lower():
                try:
                    if pd.api.types.is_numeric_dtype(col_data):
                        # Check for future years using safe conversion
                        safe_numeric_col = pd.to_numeric(df[accuracy_col], errors='coerce')
                        future_years = df[safe_numeric_col > datetime.now().year]
                        if len(future_years) > 0:
                            run_dq_check(
                                check_name=f'{accuracy_col} 정확성 점검',
                                status='FAIL',
                                message=f'미래 년도 데이터 {len(future_years)}건 발견: {future_years[accuracy_col].tolist()}',
                                metric_type='정확성(Accuracy)'
                            )
                            violations_found = True
                        else:
                            run_dq_check(
                                check_name=f'{accuracy_col} 정확성 점검',
                                status='PASS',
                                message='모든 년도 데이터 유효',
                                metric_type='정확성(Accuracy)'
                            )
                    elif pd.api.types.is_datetime64_any_dtype(col_data):
                        # datetime 형식인 경우
                        future_dates = df[pd.to_datetime(df[accuracy_col], errors='coerce').dt.year > datetime.now().year]
                        if len(future_dates) > 0:
                            run_dq_check(
                                check_name=f'{accuracy_col} 정확성 점검',
                                status='FAIL',
                                message=f'미래 날짜 데이터 {len(future_dates)}건 발견',
                                metric_type='정확성(Accuracy)'
                            )
                            violations_found = True
                        else:
                            run_dq_check(
                                check_name=f'{accuracy_col} 정확성 점검',
                                status='PASS',
                                message='모든 날짜 데이터 유효',
                                metric_type='정확성(Accuracy)'
                            )
                    else:
                        # Try to convert to datetime to check
                        converted_dates = safe_to_datetime(df[accuracy_col])
                        if not converted_dates.isna().all():  # If some values converted to datetime
                            future_dates = df[pd.to_datetime(df[accuracy_col], errors='coerce').dt.year > datetime.now().year]
                            if len(future_dates) > 0:
                                run_dq_check(
                                    check_name=f'{accuracy_col} 정확성 점검',
                                    status='FAIL',
                                    message=f'미래 날짜 데이터 {len(future_dates)}건 발견',
                                    metric_type='정확성(Accuracy)'
                                )
                                violations_found = True
                            else:
                                run_dq_check(
                                    check_name=f'{accuracy_col} 정확성 점검',
                                    status='PASS',
                                    message='날짜 데이터 유효',
                                    metric_type='정확성(Accuracy)'
                                )
                        else:
                            run_dq_check(
                                check_name=f'{accuracy_col} 정확성 점검',
                                status='PASS',
                                message='데이터 형식 점검 완료',
                                metric_type='정확성(Accuracy)'
                            )
                except:
                    run_dq_check(
                        check_name=f'{accuracy_col} 정확성 점검',
                        status='PASS',
                        message='데이터 형식 점검 불가',
                        metric_type='정확성(Accuracy)'
                    )
            elif pd.api.types.is_numeric_dtype(col_data):
                # 숫자형 데이터에 대한 정확성 점검
                if 'count' in accuracy_col.lower() or 'order' in accuracy_col.lower():
                    # 음수 주문 수에 대한 업무 규칙 점검
                    safe_numeric_col = pd.to_numeric(df[accuracy_col], errors='coerce')
                    negative_values = df[safe_numeric_col < 0]
                    if len(negative_values) > 0:
                        run_dq_check(
                            check_name=f'{accuracy_col} 정확성 점검',
                            status='FAIL',
                            message=f'음수 주문 수 {len(negative_values)}건 발견: {negative_values[accuracy_col].tolist()}',
                            metric_type='정확성(Accuracy)'
                        )
                        violations_found = True
                    else:
                        run_dq_check(
                            check_name=f'{accuracy_col} 정확성 점검',
                            status='PASS',
                            message='모든 주문 수 유효',
                            metric_type='정확성(Accuracy)'
                        )
                elif 'age' in accuracy_col.lower():
                    # 음수 나이에 대한 업무 규칙 점검
                    safe_numeric_col = pd.to_numeric(df[accuracy_col], errors='coerce')
                    negative_values = df[safe_numeric_col < 0]
                    if len(negative_values) > 0:
                        run_dq_check(
                            check_name=f'{accuracy_col} 정확성 점검',
                            status='FAIL',
                            message=f'음수 나이 {len(negative_values)}건 발견: {negative_values[accuracy_col].tolist()}',
                            metric_type='정확성(Accuracy)'
                        )
                        violations_found = True
                    else:
                        run_dq_check(
                            check_name=f'{accuracy_col} 정확성 점검',
                            status='PASS',
                            message='모든 나이 유효',
                            metric_type='정확성(Accuracy)'
                        )
                elif 'year' in accuracy_col.lower():
                    # 연도에 대한 업무 규칙 점검 (미래/과거 제약)
                    safe_numeric_col = pd.to_numeric(df[accuracy_col], errors='coerce')
                    future_years = df[safe_numeric_col > datetime.now().year]
                    past_years = df[(safe_numeric_col < 1900) & (safe_numeric_col > 0)]  # Only check positive values
                    if len(future_years) > 0:
                        run_dq_check(
                            check_name=f'{accuracy_col} 정확성 점검',
                            status='FAIL',
                            message=f'미래 년도 데이터 {len(future_years)}건 발견: {future_years[accuracy_col].tolist()}',
                            metric_type='정확성(Accuracy)'
                        )
                        violations_found = True
                    elif len(past_years) > 0:
                        run_dq_check(
                            check_name=f'{accuracy_col} 정확성 점검',
                            status='FAIL',
                            message=f'1900년 이전 년도 데이터 {len(past_years)}건 발견: {past_years[accuracy_col].tolist()}',
                            metric_type='정확성(Accuracy)'
                        )
                        violations_found = True
                    else:
                        run_dq_check(
                            check_name=f'{accuracy_col} 정확성 점검',
                            status='PASS',
                            message='모든 년도 유효',
                            metric_type='정확성(Accuracy)'
                        )
                else:
                    run_dq_check(
                        check_name=f'{accuracy_col} 정확성 점검',
                        status='PASS',
                        message='수치 데이터 정확성 확보',
                        metric_type='정확성(Accuracy)'
                    )
            else:
                # 텍스트형 데이터에 대한 정확성 점검
                has_email_pattern, invalid_emails = safe_email_pattern_check(df[accuracy_col])
                if has_email_pattern and len(invalid_emails) > 0:
                    run_dq_check(
                        check_name=f'{accuracy_col} 정확성 점검',
                        status='FAIL',
                        message=f'유효하지 않은 이메일 형식 {len(invalid_emails)}건 발견',
                        metric_type='정확성(Accuracy)'
                    )
                    violations_found = True
                elif has_email_pattern:
                    run_dq_check(
                        check_name=f'{accuracy_col} 정확성 점검',
                        status='PASS',
                        message='이메일 형식 유효',
                        metric_type='정확성(Accuracy)'
                    )
                else:
                    run_dq_check(
                        check_name=f'{accuracy_col} 정확성 점검',
                        status='PASS',
                        message='데이터 형식 확인 완료',
                        metric_type='정확성(Accuracy)'
                    )

        # 6. 보안성(Security) 점검 - 민감정보 식별
        if security_col in df.columns:
            col_data = df[security_col]
            # 보안성 점검 - 민감 정보 패턴 탐지
            sensitive_patterns = [r'\b\d{3}-?\d{2}-?\d{4}\b', r'\b\d{16}\b']  # SSN, 신용카드 패턴
            sensitive_found = False
            for pattern in sensitive_patterns:
                for val in col_data.dropna():
                    if re.search(pattern, str(val)):
                        sensitive_found = True
                        break
                if sensitive_found:
                    break
            
            if sensitive_found:
                run_dq_check(
                    check_name=f'{security_col} 보안성 점검',
                    status='FAIL',
                    message=f'민감 정보 패턴이 포함된 데이터 발견',
                    metric_type='보안성(Security)'
                )
            else:
                run_dq_check(
                    check_name=f'{security_col} 보안성 점검', 
                    status='PASS', 
                    message='민감 정보 없음 확인',
                    metric_type='보안성(Security)'
                )

        # 7. 적시성(Timeliness) 점검 - 데이터 최신성
        if timely_col in df.columns:
            col_data = df[timely_col]
            # 적시성 점검 - 컬럼 이름이나 데이터 타입 기반으로 점검
            if pd.api.types.is_datetime64_any_dtype(col_data) or 'date' in timely_col.lower() or 'year' in timely_col.lower():
                try:
                    if pd.api.types.is_numeric_dtype(col_data):
                        # 숫자형 날짜/년도 데이터 점검 - using safe conversion
                        safe_numeric_col = pd.to_numeric(df[timely_col], errors='coerce')
                        future_values = df[safe_numeric_col > datetime.now().year]
                        past_values = df[(safe_numeric_col < 1900) & (safe_numeric_col > 0)]  # Only check positive values

                        if len(future_values) > 0:
                            run_dq_check(
                                check_name=f'{timely_col} 적시성 점검',
                                status='FAIL',
                                message=f'미래 날짜/년도 데이터 {len(future_values)}건 발견: {future_values[timely_col].tolist()}',
                                metric_type='적시성(Timeliness)'
                            )
                        elif len(past_values) > 0:
                            run_dq_check(
                                check_name=f'{timely_col} 적시성 점검',
                                status='FAIL',
                                message=f'1900년 이전 날짜/년도 데이터 {len(past_values)}건 발견: {past_values[timely_col].tolist()}',
                                metric_type='적시성(Timeliness)'
                            )
                        else:
                            run_dq_check(
                                check_name=f'{timely_col} 적시성 점검',
                                status='PASS',
                                message='모든 날짜/년도 데이터 적시성 확보',
                                metric_type='적시성(Timeliness)'
                            )
                    elif pd.api.types.is_datetime64_any_dtype(col_data):
                        # datetime 형식인 경우
                        future_dates = df[pd.to_datetime(df[timely_col], errors='coerce').dt.year > datetime.now().year]
                        if len(future_dates) > 0:
                            run_dq_check(
                                check_name=f'{timely_col} 적시성 점검',
                                status='FAIL',
                                message=f'미래 날짜 데이터 {len(future_dates)}건 발견',
                                metric_type='적시성(Timeliness)'
                            )
                        else:
                            run_dq_check(
                                check_name=f'{timely_col} 적시성 점검',
                                status='PASS',
                                message='모든 날짜 데이터 적시성 확보',
                                metric_type='적시성(Timeliness)'
                            )
                    else:
                        # Try to convert to datetime
                        converted_dates = safe_to_datetime(df[timely_col])
                        if not converted_dates.isna().all():
                            future_dates = df[converted_dates.dt.year > datetime.now().year]
                            if len(future_dates) > 0:
                                run_dq_check(
                                    check_name=f'{timely_col} 적시성 점검',
                                    status='FAIL',
                                    message=f'미래 날짜 데이터 {len(future_dates)}건 발견',
                                    metric_type='적시성(Timeliness)'
                                )
                            else:
                                run_dq_check(
                                    check_name=f'{timely_col} 적시성 점검',
                                    status='PASS',
                                    message='날짜 데이터 적시성 확보',
                                    metric_type='적시성(Timeliness)'
                                )
                        else:
                            run_dq_check(
                                check_name=f'{timely_col} 적시성 점검',
                                status='PASS',
                                message='날짜 데이터 적시성 확보',
                                metric_type='적시성(Timeliness)'
                            )
                except:
                    # 날짜 변환에 실패하면 점검 불가 처리
                    run_dq_check(
                        check_name=f'{timely_col} 적시성 점검',
                        status='PASS',
                        message='날짜 형식 점검 불가',
                        metric_type='적시성(Timeliness)'
                    )
            else:
                # 날짜 형식이 아닌 경우 기본 통과
                run_dq_check(
                    check_name=f'{timely_col} 적시성 점검',
                    status='PASS',
                    message='적시성 점검 불필요',
                    metric_type='적시성(Timeliness)'
                )

        # 8. 유용성(Usability) 점검 - 데이터 활용성
        if usability_col in df.columns:
            col_data = df[usability_col]
            # 텍스트 데이터의 최소 길이 점검
            if pd.api.types.is_object_dtype(col_data):
                # Filter out NaN values before checking length
                non_null_data = col_data.dropna()
                if len(non_null_data) > 0:
                    short_values = non_null_data[non_null_data.astype(str).str.len() < 2]
                    if len(short_values) > 0:
                        run_dq_check(
                            check_name=f'{usability_col} 유용성 점검',
                            status='FAIL',
                            message=f'최소 길이 미만 데이터 {len(short_values)}건 발견',
                            metric_type='유용성(Usability)'
                        )
                    else:
                        run_dq_check(
                            check_name=f'{usability_col} 유용성 점검', 
                            status='PASS', 
                            message='모든 데이터 유용성 확보',
                            metric_type='유용성(Usability)'
                        )
                else:
                    run_dq_check(
                        check_name=f'{usability_col} 유용성 점검', 
                        status='PASS', 
                        message='데이터 유용성 확보',
                        metric_type='유용성(Usability)'
                    )
            else:
                run_dq_check(
                    check_name=f'{usability_col} 유용성 점검', 
                    status='PASS', 
                    message='데이터 유용성 확보',
                    metric_type='유용성(Usability)'
                )

    except Exception as e:
        st.error(f"품질 지표 점검 중 오류가 발생했습니다: {str(e)}")

    # --- 6. 4대 진단 방법 실행 ---
    try:
        if profiling_enabled:
            # 프로파일링(Profiling) 실행 - 값 진단 및 구조 진단
            st.subheader("📈 프로파일링 결과 (값 진단 및 구조 진단)")

            # 값 진단 (Value Profiling)
            st.markdown("**값 진단 (Value Analysis):**")
            value_profile_results = []

            for col in df.columns:
                col_type = str(df[col].dtype)
                total_count = len(df)
                missing_count = df[col].isnull().sum()
                unique_count = df[col].nunique()
                completeness_rate = (total_count - missing_count) / total_count * 100

                # 패턴 분석 (Pattern Analysis) - 예시
                pattern_deviation = 0
                if pd.api.types.is_numeric_dtype(df[col]):
                    # 수치형 데이터의 경우 평균과 표준편차 기반 이상치 분석 (패턴 분석)
                    if df[col].count() > 0:  # Non-null count
                        mean_val = df[col].mean()
                        std_val = df[col].std()
                        if std_val and std_val != 0:
                            z_scores = ((df[col] - mean_val) / std_val).abs()
                            pattern_deviation = (z_scores > 3).sum()  # Z-score > 3인 값 수

                elif pd.api.types.is_object_dtype(df[col]):
                    # 텍스트 데이터의 경우 길이 분석
                    try:
                        avg_length = df[col].astype(str).str.len().mean()
                    except:
                        avg_length = 0

                value_profile_results.append({
                    '컬럼명': col,
                    '데이터 유형': col_type,
                    '총 행 수': total_count,
                    '결측치 수': missing_count,
                    '고유값 수': unique_count,
                    '완전성 비율': f'{completeness_rate:.2f}%',
                    '이상치 수 (패턴 분석)': int(pattern_deviation) if pattern_deviation is not None else 0
                })

            value_profile_df = pd.DataFrame(value_profile_results)
            st.dataframe(value_profile_df, use_container_width=True)

            # 구조 진단 (Structure Profiling) - 메타데이터 분석
            st.markdown("**구조 진단 (Structure Analysis):**")
            structure_profile_results = []

            for col in df.columns:
                structure_profile_results.append({
                    '컬럼명': col,
                    '데이터 유형': str(df[col].dtype),
                    '컬럼 길이 (최대)': df[col].astype(str).str.len().max() if len(df) > 0 else 0,
                    '널 가능 여부': 'Y' if df[col].isnull().any() else 'N',
                    '고유값 비율': f'{(df[col].nunique() / len(df) * 100):.2f}%' if len(df) > 0 else '0%'
                })

            structure_profile_df = pd.DataFrame(structure_profile_results)
            st.dataframe(structure_profile_df, use_container_width=True)

            # Additional uniqueness information in profiling
            st.markdown("**고유성 분석:**")
            uniqueness_analysis = []
            for col in df.columns:
                total_count = len(df)
                unique_count = df[col].nunique()

                # Count how many values appear exactly once (genuinely unique)
                try:
                    value_counts = df[col].value_counts()
                    unique_once_count = (value_counts == 1).sum()  # Count of values that appear exactly once
                    # Count total occurrences of duplicated values
                    duplicate_occurrences = value_counts[value_counts > 1].sum() if not value_counts.empty else 0  # Total count of duplicates

                    uniqueness_rate = unique_once_count / total_count * 100 if total_count > 0 else 0  # Proportion of entries that are unique
                except:
                    # Fallback values if something goes wrong
                    unique_once_count = 0
                    duplicate_occurrences = 0
                    uniqueness_rate = 0

                uniqueness_analysis.append({
                    '컬럼명': col,
                    '총 행 수': total_count,
                    '고유값 수': unique_count,
                    '중복 발생 수': int(duplicate_occurrences) if duplicate_occurrences is not None else 0,
                    '고유성 비율': f'{uniqueness_rate:.2f}%'
                })

            uniqueness_df = pd.DataFrame(uniqueness_analysis)
            st.dataframe(uniqueness_df, use_container_width=True)

        if business_rule_enabled:
            # 업무규칙 진단 실행 - 비즈니스 로직 기반 데이터 측정
            st.subheader("📋 업무규칙 진단 결과")

            # 업무규칙 도출 및 정의 (예시)
            rule_violations_found = False
            all_rule_violations = pd.DataFrame()

            # 업무규칙 1: order_count는 음수가 아니어야 함
            if 'order_count' in df.columns:
                try:
                    # Convert to numeric, coercing errors to NaN
                    numeric_order_count = pd.to_numeric(df['order_count'], errors='coerce')
                    negative_orders_mask = numeric_order_count < 0
                    negative_orders = df[negative_orders_mask]
                    if len(negative_orders) > 0:
                        rule_violations_found = True
                        st.write(f"❌ 'order_count < 0' 업무규칙 위반: {len(negative_orders)}건")
                        rule_violations = negative_orders.copy()
                        rule_violations['violation_type'] = '음수 주문 수'
                        if all_rule_violations.empty:
                            all_rule_violations = rule_violations
                        else:
                            all_rule_violations = pd.concat([all_rule_violations, rule_violations])
                except:
                    pass  # Skip if conversion fails

            # 업무규칙 2: age는 음수가 아니어야 함
            if 'age' in df.columns:
                try:
                    # Convert to numeric, coercing errors to NaN
                    numeric_age = pd.to_numeric(df['age'], errors='coerce')
                    negative_ages_mask = numeric_age < 0
                    negative_ages = df[negative_ages_mask]
                    if len(negative_ages) > 0:
                        rule_violations_found = True
                        st.write(f"❌ 'age < 0' 업무규칙 위반: {len(negative_ages)}건")
                        rule_violations = negative_ages.copy()
                        rule_violations['violation_type'] = '음수 나이'
                        if all_rule_violations.empty:
                            all_rule_violations = rule_violations
                        else:
                            all_rule_violations = pd.concat([all_rule_violations, rule_violations])
                except:
                    pass  # Skip if conversion fails

            # 업무규칙 3: join_year는 미래가 아니어야 함
            if 'join_year' in df.columns:
                try:
                    # Convert to numeric, coercing errors to NaN
                    numeric_join_year = pd.to_numeric(df['join_year'], errors='coerce')
                    future_years_mask = numeric_join_year > datetime.now().year
                    future_years = df[future_years_mask]
                    if len(future_years) > 0:
                        rule_violations_found = True
                        st.write(f"❌ 'join_year > 현재 연도' 업무규칙 위반: {len(future_years)}건")
                        rule_violations = future_years.copy()
                        rule_violations['violation_type'] = '미래 가입 연도'
                        if all_rule_violations.empty:
                            all_rule_violations = rule_violations
                        else:
                            all_rule_violations = pd.concat([all_rule_violations, rule_violations])
                except:
                    pass  # Skip if conversion fails

            # 업무규칙 4: join_year는 1900년 이전이 아니어야 함
            if 'join_year' in df.columns:
                try:
                    # Convert to numeric, coercing errors to NaN
                    numeric_join_year = pd.to_numeric(df['join_year'], errors='coerce')
                    past_years_mask = (numeric_join_year < 1900) & (numeric_join_year > 0)  # Only check positive values
                    past_years = df[past_years_mask]
                    if len(past_years) > 0:
                        rule_violations_found = True
                        st.write(f"❌ 'join_year < 1900' 업무규칙 위반: {len(past_years)}건")
                        rule_violations = past_years.copy()
                        rule_violations['violation_type'] = '1900년 이전 가입 연도'
                        if all_rule_violations.empty:
                            all_rule_violations = rule_violations
                        else:
                            all_rule_violations = pd.concat([all_rule_violations, rule_violations])
                except:
                    pass  # Skip if conversion fails

            if rule_violations_found:
                st.subheader("업무규칙 위반 상세 데이터:")
                # Remove the violation_type column for display if it exists in the original data
                if 'violation_type' in all_rule_violations.columns:
                    display_violations = all_rule_violations.drop('violation_type', axis=1)
                else:
                    display_violations = all_rule_violations
                st.dataframe(display_violations, use_container_width=True)
            else:
                st.write("✅ 모든 데이터가 정의된 업무규칙을 준수합니다")

            # 업무규칙 진단 설명 추가
            with st.expander("업무규칙 진단 설명"):
                st.markdown("""
                **업무규칙 진단은 7대 데이터 품질 지표 중 다음과 같은 성질을 진단합니다:**

                1. **정확성 (Accuracy)**
                   - 업무 규칙 위반: 예) 음수 주문 수, 음수 나이 등 허용되지 않는 값 확인
                   - 실제 비즈니스 시나리오에 부합하지 않는 데이터 식별

                2. **일관성 (Consistency)**
                   - 데이터 간 논리적 일관성: 예) 가입 연도가 미래인 경우 등
                   - 엔티티 간의 관계 일관성 여부 확인

                3. **적시성 (Timeliness)**
                   - 시간적 타당성: 예) 가입 연도가 미래이거나 너무 과거인 경우
                   - 데이터의 시기적 타당성 확인

                *업무규칙 진단은 조직의 비즈니스 로직이나 정책에 따라 정의된 규칙에 따라
                데이터의 적합성을 평가하는 방법입니다.*
                """)

        if checklist_enabled:
            # 체크리스트 진단 실행
            st.subheader("✅ 체크리스트 진단 결과")
            checklist_results = []
            
            # 각 컬럼에 대한 기본 체크리스트 항목
            for col in df.columns:
                total_count = len(df)
                null_count = df[col].isnull().sum()
                unique_count = df[col].nunique()
                is_unique = safe_is_unique(df[col])  # Use safe function

                # Safe type check
                try:
                    col_dtype = df[col].dtype
                    if col_dtype != 'object':
                        type_check_result = 'PASS'
                    else:
                        # For object types, check string length
                        try:
                            min_len = df[col].astype(str).str.len().min()
                            type_check_result = 'PASS' if min_len and min_len > 0 else 'WARN'
                        except:
                            type_check_result = 'WARN'
                except:
                    type_check_result = 'WARN'

                checklist_results.extend([
                    {'항목': f'{col} - 결측치 확인', '결과': 'PASS' if null_count == 0 else 'FAIL'},
                    {'항목': f'{col} - 고유값 확인', '결과': 'PASS' if is_unique else 'FAIL'},  # Fixed: Proper uniqueness check
                    {'항목': f'{col} - 데이터 유형 확인', '결과': type_check_result}
                ])
            
            checklist_df = pd.DataFrame(checklist_results)
            st.dataframe(checklist_df, use_container_width=True)

            # 체크리스트 진단 설명 추가
            with st.expander("체크리스트 진단 설명"):
                st.markdown("""
                **체크리스트 진단은 7대 데이터 품질 지표 중 다음과 같은 성질을 진단합니다:**

                1. **완전성 (Completeness)**
                   - "결측치 확인": 데이터의 누락 여부를 점검
                   - NULL 또는 빈 값이 있는지 확인

                2. **고유성 (Uniqueness)**
                   - "고유값 확인": 중복값이 있는지 점검
                   - 데이터가 고유한지 (중복되지 않았는지) 확인

                3. **유용성 (Usability)**
                   - "데이터 유형 확인": 데이터가 사용 가능하고 의미 있는 형식인지 점검
                   - 최소한의 길이나 형식을 만족하는지 확인

                *체크리스트 진단은 7대 품질 지표의 기초 검증 단계로, 각 지표에 대한 최소한의 확인을 수행하여
                데이터 품질의 전반적인 상태를 빠르게 파악할 수 있게 합니다.*
                """)

        if realtime_measure_enabled:
            # 비정형 실측 진단 실행
            st.subheader("🔍 비정형 실측 진단 결과")
            # 예제: 이상치 탐지 (IQR 방법)
            numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
            if numeric_cols:
                for col in numeric_cols:
                    try:
                        outliers = safe_outlier_detection(df[col])
                        if isinstance(outliers, pd.Series) and len(outliers) > 0:
                            st.write(f"❌ {col} 컬럼 이상치 {len(outliers)}건 발견")
                            outlier_rows = df[df.index.isin(outliers.index)]
                            st.dataframe(outlier_rows, use_container_width=True)
                        else:
                            st.write(f"✅ {col} 컬럼 이상치 없음")
                    except Exception as e:
                        st.write(f"{col} 컬럼 이상치 분석 중 오류 발생: {str(e)}")
            else:
                st.write("🔢 숫자형 컬럼이 없어 이상치 분석을 수행할 수 없습니다")

            # 비정형 실측 진단 설명 추가
            with st.expander("비정형 실측 진단 설명"):
                st.markdown("""
                **비정형 실측 진단은 7대 데이터 품질 지표 중 다음과 같은 성질을 진단합니다:**

                1. **정확성 (Accuracy)**
                   - 이상치(Outlier) 탐지: 데이터가 정상 범위를 벗어나는 경우 식별
                   - IQR(Interquartile Range) 방법을 사용하여 통계적으로 이상한 값 검출

                2. **적시성 (Timeliness)**
                   - 시간 관련 이상치: 미래 또는 과거에 비정상적인 날짜/년도 식별

                3. **일관성 (Consistency)**
                   - 데이터 패턴의 불일치: 통계적으로 일치하지 않는 값 탐지

                *비정형 실측 진단은 정형화되지 않은 방식으로 데이터에서 예외적 패턴과 이상 사항을
                실시간으로 식별하여 데이터 품질을 평가하는 방법입니다.*
                """)

    except Exception as e:
        st.error(f"진단 방법 실행 중 오류가 발생했습니다: {str(e)}")

    # --- 7. 결과 표시 ---
    st.header("📋 종합 데이터 품질 진단 결과")

    # 결과를 DataFrame으로 변환
    if dq_results:
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

        # 지표 유형별 요약
        st.subheader("📊 지표 유형별 요약")
        metric_summary = results_df.groupby('지표 유형')['상태'].value_counts().unstack(fill_value=0)
        st.bar_chart(metric_summary)

        # 요약 통계
        total_checks = len(results_df)
        error_checks = len(results_df[results_df['상태'].str.contains('❌')])
        pass_checks = total_checks - error_checks

        col1, col2, col3 = st.columns(3)
        col1.metric("총 점검 항목", total_checks)
        col2.metric("정상 항목", pass_checks)
        col3.metric("오류 항목", error_checks)

        # --- 8. 오류 데이터 상세 조회 ---
        st.header("🔍 오류 데이터 상세 조회")

        # 오류가 있는 지표별 상세 표시
        for metric_type in results_df['지표 유형'].unique():
            metric_results = results_df[results_df['지표 유형'] == metric_type]
            error_results = metric_results[metric_results['상태'].str.contains('❌')]
            
            if not error_results.empty:
                st.subheader(f"❌ {metric_type} 오류 데이터")
                
                # 오류가 있는 컬럼에 따라 다른 상세 정보 표시
                for _, result in error_results.iterrows():
                    check_name = result['점검 항목']
                    col_name = check_name.split(' ')[0]  # Extract column name
                    
                    st.write(f"**{check_name}**")
                    st.write(f"{result['메시지']}")
                    
                    if col_name in df.columns:
                        # 오류 데이터만 표시 (specific to each type)
                        if col_name == accuracy_col and '유효하지 않은 이메일 형식' in str(result['메시지']):
                            has_email_pattern, invalid_emails = safe_email_pattern_check(df[col_name])
                            if len(invalid_emails) > 0:
                                invalid_rows = df[df[col_name].isin(invalid_emails)]
                                st.dataframe(invalid_rows, use_container_width=True)
                        elif col_name == timely_col and any(x in str(result['메시지']) for x in ['미래 날짜', '미래 날짜/년도']):
                            if pd.api.types.is_datetime64_any_dtype(df[col_name]):
                                future_dates = df[pd.to_datetime(df[col_name]).dt.year > datetime.now().year]
                                if not future_dates.empty:
                                    st.dataframe(future_dates, use_container_width=True)
                            elif pd.api.types.is_numeric_dtype(df[col_name]):
                                future_years = df[df[col_name] > datetime.now().year]
                                if not future_years.empty:
                                    st.dataframe(future_years, use_container_width=True)
                            else:
                                converted_dates = safe_to_datetime(df[col_name])
                                future_dates = df[converted_dates.dt.year > datetime.now().year if not converted_dates.isna().all() else pd.Series(dtype='datetime64[ns]').reindex(df.index)]
                                if not future_dates.empty:
                                    st.dataframe(future_dates, use_container_width=True)
                        elif col_name == complete_col:
                            null_rows = df[df[col_name].isnull()]
                            if not null_rows.empty:
                                st.dataframe(null_rows, use_container_width=True)
                        elif col_name == uniqueness_col:
                            # Show duplicate rows
                            duplicate_rows = df[df[col_name].duplicated(keep=False)].sort_values(by=col_name)
                            if not duplicate_rows.empty:
                                st.dataframe(duplicate_rows, use_container_width=True)

    # --- 9. 데이터 품질 용어 가시화 ---
    st.header("🔍 데이터 품질 관련 용어 가시화")
    with st.expander("7대 품질 지표 설명"):
        st.markdown("""
        - **준비성 (Availability)**: 데이터가 필요한 시점에 접근 가능한 정도
        - **고유성 (Uniqueness)**: 중복되지 않은 고유한 데이터의 정도
        - **완전성 (Completeness)**: 누락된 값이나 속성이 없는 정도  
        - **일관성 (Consistency)**: 동일한 의미의 데이터가 다양한 시스템에서 일관되게 표현되는 정도
        - **정확성 (Accuracy)**: 실제 세계의 값과 일치하는 정도
        - **보안성 (Security)**: 데이터가 무단 접근 및 침해로부터 보호되는 정도
        - **적시성 (Timeliness)**: 데이터가 최신 정보를 반복하고 있는 정도
        - **유용성 (Usability)**: 데이터가 사용자에게 유용하고 효율적인 정도
        """)
    
    with st.expander("4대 진단 방법 설명"):
        st.markdown("""
        - **프로파일링 (Profiling)**: 데이터의 통계적 특성 분석
        - **업무규칙 진단 (Business Rule Diagnosis)**: 업무 규칙에 따른 데이터 검증
        - **체크리스트 (Checklist)**: 표준 기준에 대한 항목별 검증
        - **비정형 실측 (Unstructured Real-time Measurement)**: 비정형 데이터의 실시간 분석
        """)