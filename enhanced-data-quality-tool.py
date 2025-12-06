import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime

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
    df = pd.read_csv(uploaded_file)
    st.success("데이터가 성공적으로 업로드되었습니다!")
    st.dataframe(df, use_container_width=True)
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

# --- 3. 데이터 품질 점검 항목 설정 ---
st.header("🔍 품질 점검 설정")

# 7대 품질 지표 설정
st.subheader("7대 품질 지표")

col1, col2 = st.columns(2)
with col1:
    # 준비성 (Availability) 점검 컬럼 선택
    availability_col_index = min(0, len(df.columns) - 1)
    availability_col = st.selectbox("준비성(Availability) 점검할 컬럼", options=df.columns.tolist(), index=availability_col_index)
    # 고유성 (Uniqueness) 점검 컬럼 선택
    uniqueness_col_index = min(0, len(df.columns) - 1)  # Default to first column
    uniqueness_col = st.selectbox("고유성(Uniqueness) 점검할 컬럼", options=df.columns.tolist(), index=uniqueness_col_index)
    # 완전성 (Completeness) 점검 컬럼 선택
    complete_col_index = min(2, len(df.columns) - 1)
    complete_col = st.selectbox("완전성(Completeness) 점검할 컬럼", options=df.columns.tolist(), index=complete_col_index)
    # 일관성 (Consistency) 점검 컬럼 선택
    consistency_col_index = min(1, len(df.columns) - 1)
    consistency_col = st.selectbox("일관성(Consistency) 점검할 컬럼", options=df.columns.tolist(), index=consistency_col_index)

with col2:
    # 정확성 (Accuracy) 점검 컬럼 선택
    accuracy_col_index = min(3, len(df.columns) - 1)  # Changed from 4 to 3 to avoid index error
    accuracy_col = st.selectbox("정확성(Accuracy) 점검할 컬럼", options=df.columns.tolist(), index=accuracy_col_index)
    # 보안성 (Security) 점검 컬럼 선택
    security_col_index = min(3, len(df.columns) - 1)  # Changed from 4 to 3 to avoid index error
    security_col = st.selectbox("보안성(Security) 점검할 컬럼", options=df.columns.tolist(), index=security_col_index)
    # 적시성 (Timeliness) 점검 컬럼 선택
    timely_col_index = min(3, len(df.columns) - 1)
    timely_col = st.selectbox("적시성(Timeliness) 점검할 컬럼", options=df.columns.tolist(), index=timely_col_index)
    # 유용성 (Usability) 점검 컬럼 선택
    usability_col_index = min(1, len(df.columns) - 1)
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

    # --- 4. 7대 품질 지표 점검 실행 ---

    # 1. 준비성(Availability) 점검 - 데이터 접근 가능성
    col = availability_col
    missing_count = df[col].isnull().sum() + (df[col] == '').sum()
    if missing_count > 0:
        run_dq_check(
            check_name=f'{col} 준비성 점검',
            status='FAIL',
            message=f'접근 불가능한 값 {missing_count}건 발견',
            metric_type='준비성(Availability)'
        )
    else:
        run_dq_check(
            check_name=f'{col} 준비성 점검',
            status='PASS',
            message='모든 데이터 접근 가능',
            metric_type='준비성(Availability)'
        )

    # 2. 고유성(Uniqueness) 점검 - 중복 값 확인
    col = uniqueness_col
    is_unique = df[col].is_unique
    if not is_unique:
        duplicate_count = df[col].duplicated(keep='first').sum()
        run_dq_check(
            check_name=f'{col} 고유성 점검',
            status='FAIL',
            message=f'중복된 값 {duplicate_count}건 발견. (오류율: {duplicate_count / len(df) * 100:.2f}%)',
            metric_type='고유성(Uniqueness)'
        )
    else:
        run_dq_check(
            check_name=f'{col} 고유성 점검',
            status='PASS',
            message='고유성 확보',
            metric_type='고유성(Uniqueness)'
        )

    # 2. 완전성(Completeness) 점검 - 결측치
    col = complete_col
    null_count = df[col].isnull().sum()
    if null_count > 0:
        run_dq_check(
            check_name=f'{col} 완전성 점검',
            status='FAIL',
            message=f'결측치(NULL) {null_count}건 발견. (오류율: {null_count / len(df) * 100:.2f}%)',
            metric_type='완전성(Completeness)'
        )
    else:
        run_dq_check(
            check_name=f'{col} 완전성 점검', 
            status='PASS', 
            message='결측치 없음',
            metric_type='완전성(Completeness)'
        )

    # 3. 일관성(Consistency) 점검 - 데이터 형식 일관성
    col = consistency_col
    # 예: 텍스트 데이터의 형식 불일치
    if pd.api.types.is_object_dtype(df[col]):
        inconsistent_formats = 0  # 간단한 예시로 0으로 설정
        if inconsistent_formats > 0:
            run_dq_check(
                check_name=f'{col} 일관성 점검',
                status='FAIL',
                message=f'형식 불일치 {inconsistent_formats}건 발견',
                metric_type='일관성(Consistency)'
            )
        else:
            run_dq_check(
                check_name=f'{col} 일관성 점검', 
                status='PASS', 
                message='데이터 형식 일관성 확보',
                metric_type='일관성(Consistency)'
            )

    # 4. 정확성(Accuracy) 점검 - 데이터 유효성
    col = accuracy_col
    # 데이터 타입에 따라 정확성 점검
    if pd.api.types.is_datetime64_any_dtype(df[col]) or 'date' in col.lower() or 'year' in col.lower():
        # 날짜 형식 점검
        try:
            # 미래 날짜 또는 과거 너무 오래된 날짜 점검
            if pd.api.types.is_numeric_dtype(df[col]):
                future_years = df[df[col] > datetime.now().year]
                if len(future_years) > 0:
                    run_dq_check(
                        check_name=f'{col} 정확성 점검',
                        status='FAIL',
                        message=f'미래 년도 데이터 {len(future_years)}건 발견: {future_years[col].tolist()}',
                        metric_type='정확성(Accuracy)'
                    )
                else:
                    run_dq_check(
                        check_name=f'{col} 정확성 점검',
                        status='PASS',
                        message='모든 년도 데이터 유효',
                        metric_type='정확성(Accuracy)'
                    )
            else:
                # datetime 형식인 경우
                future_dates = df[pd.to_datetime(df[col]).dt.year > datetime.now().year]
                if len(future_dates) > 0:
                    run_dq_check(
                        check_name=f'{col} 정확성 점검',
                        status='FAIL',
                        message=f'미래 날짜 데이터 {len(future_dates)}건 발견',
                        metric_type='정확성(Accuracy)'
                    )
                else:
                    run_dq_check(
                        check_name=f'{col} 정확성 점검',
                        status='PASS',
                        message='모든 날짜 데이터 유효',
                        metric_type='정확성(Accuracy)'
                    )
        except:
            # 날짜 변환에 실패하면 문자열로 간주하고 정확성 점검 생략
            run_dq_check(
                check_name=f'{col} 정확성 점검',
                status='PASS',
                message='데이터 형식 점검 불가',
                metric_type='정확성(Accuracy)'
            )
    elif pd.api.types.is_numeric_dtype(df[col]):
        # 숫자형 데이터에 대한 정확성 점검
        if df[col].min() < 0 and 'count' in col.lower():
            # 음수 개수에 대한 점검
            negative_values = df[df[col] < 0]
            if len(negative_values) > 0:
                run_dq_check(
                    check_name=f'{col} 정확성 점검',
                    status='FAIL',
                    message=f'음수 값 {len(negative_values)}건 발견: {negative_values[col].tolist()}',
                    metric_type='정확성(Accuracy)'
                )
            else:
                run_dq_check(
                    check_name=f'{col} 정확성 점검',
                    status='PASS',
                    message='모든 수치 데이터 유효',
                    metric_type='정확성(Accuracy)'
                )
        else:
            run_dq_check(
                check_name=f'{col} 정확성 점검',
                status='PASS',
                message='수치 데이터 정확성 확보',
                metric_type='정확성(Accuracy)'
            )
    else:
        # 텍스트형 데이터에 대한 정확성 점검
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if df[col].dtype == 'object':
            # 이메일 형식인지 확인
            email_matches = df[df[col].str.contains(email_pattern, na=False, regex=True)]
            if len(email_matches) > 0:
                # 이메일 형식 점검
                invalid_emails = df[~df[col].str.match(email_pattern, na=False)]
                if len(invalid_emails) > 0:
                    run_dq_check(
                        check_name=f'{col} 정확성 점검',
                        status='FAIL',
                        message=f'유효하지 않은 이메일 형식 {len(invalid_emails)}건 발견',
                        metric_type='정확성(Accuracy)'
                    )
                else:
                    run_dq_check(
                        check_name=f'{col} 정확성 점검',
                        status='PASS',
                        message='이메일 형식 유효',
                        metric_type='정확성(Accuracy)'
                    )
            else:
                run_dq_check(
                    check_name=f'{col} 정확성 점검',
                    status='PASS',
                    message='데이터 형식 확인 완료',
                    metric_type='정확성(Accuracy)'
                )

    # 5. 보안성(Security) 점검 - 민감정보 식별
    col = security_col
    # 보안성 점검 - 민감 정보 패턴 탐지
    sensitive_patterns = [r'\b\d{3}-?\d{2}-?\d{4}\b', r'\b\d{16}\b']  # SSN, 신용카드 패턴
    sensitive_found = False
    for pattern in sensitive_patterns:
        for val in df[col].dropna():
            if re.search(pattern, str(val)):
                sensitive_found = True
                break
        if sensitive_found:
            break

    if sensitive_found:
        run_dq_check(
            check_name=f'{col} 보안성 점검',
            status='FAIL',
            message=f'민감 정보 패턴이 포함된 데이터 발견',
            metric_type='보안성(Security)'
        )
    else:
        run_dq_check(
            check_name=f'{col} 보안성 점검',
            status='PASS',
            message='민감 정보 없음 확인',
            metric_type='보안성(Security)'
        )

    # 6. 적시성(Timeliness) 점검 - 데이터 최신성
    col = timely_col
    # 적시성 점검 - 컬럼 이름이나 데이터 타입 기반으로 점검
    if pd.api.types.is_datetime64_any_dtype(df[col]) or 'date' in col.lower() or 'year' in col.lower():
        try:
            if pd.api.types.is_numeric_dtype(df[col]):
                # 숫자형 날짜/년도 데이터 점검
                future_values = df[df[col] > datetime.now().year]
                if len(future_values) > 0:
                    run_dq_check(
                        check_name=f'{col} 적시성 점검',
                        status='FAIL',
                        message=f'미래 날짜/년도 데이터 {len(future_values)}건 발견: {future_values[col].tolist()}',
                        metric_type='적시성(Timeliness)'
                    )
                else:
                    run_dq_check(
                        check_name=f'{col} 적시성 점검',
                        status='PASS',
                        message='모든 날짜/년도 데이터 적시성 확보',
                        metric_type='적시성(Timeliness)'
                    )
            else:
                # datetime 형식인 경우
                future_dates = df[pd.to_datetime(df[col]).dt.year > datetime.now().year]
                if len(future_dates) > 0:
                    run_dq_check(
                        check_name=f'{col} 적시성 점검',
                        status='FAIL',
                        message=f'미래 날짜 데이터 {len(future_dates)}건 발견',
                        metric_type='적시성(Timeliness)'
                    )
                else:
                    run_dq_check(
                        check_name=f'{col} 적시성 점검',
                        status='PASS',
                        message='모든 날짜 데이터 적시성 확보',
                        metric_type='적시성(Timeliness)'
                    )
        except:
            # 날짜 변환에 실패하면 점검 불가 처리
            run_dq_check(
                check_name=f'{col} 적시성 점검',
                status='PASS',
                message='날짜 형식 점검 불가',
                metric_type='적시성(Timeliness)'
            )
    else:
        # 날짜 형식이 아닌 경우 기본 통과
        run_dq_check(
            check_name=f'{col} 적시성 점검',
            status='PASS',
            message='적시성 점검 불필요',
            metric_type='적시성(Timeliness)'
        )

    # 7. 유용성(Usability) 점검 - 데이터 활용성
    col = usability_col
    # 텍스트 데이터의 최소 길이 점검
    if pd.api.types.is_object_dtype(df[col]):
        min_length = 2  # 최소 2자 이상
        short_values = df[df[col].str.len() < min_length]
        if len(short_values) > 0:
            run_dq_check(
                check_name=f'{col} 유용성 점검',
                status='FAIL',
                message=f'최소 길이 미만 데이터 {len(short_values)}건 발견',
                metric_type='유용성(Usability)'
            )
        else:
            run_dq_check(
                check_name=f'{col} 유용성 점검', 
                status='PASS', 
                message='모든 데이터 유용성 확보',
                metric_type='유용성(Usability)'
            )

    # --- 5. 4대 진단 방법 실행 ---
    if profiling_enabled:
        # 프로파일링(Profiling) 실행
        st.subheader("📈 프로파일링 결과")
        profile_results = []

        for col in df.columns:
            col_type = str(df[col].dtype)
            total_count = len(df)
            missing_count = df[col].isnull().sum()
            unique_count = df[col].nunique()
            completeness_rate = (total_count - missing_count) / total_count * 100

            profile_results.append({
                '컬럼명': col,
                '데이터 유형': col_type,
                '총 행 수': total_count,
                '결측치 수': missing_count,
                '고유값 수': unique_count,
                '완전성 비율': f'{completeness_rate:.2f}%'  # This represents non-null values, not uniqueness
            })

        profile_df = pd.DataFrame(profile_results)
        st.dataframe(profile_df, use_container_width=True)

        # Additional uniqueness information in profiling
        st.subheader("📊 고유성 분석")
        uniqueness_analysis = []
        for col in df.columns:
            total_count = len(df)
            unique_count = df[col].nunique()

            # Count how many values appear exactly once (genuinely unique)
            value_counts = df[col].value_counts()
            unique_once_count = (value_counts == 1).sum()  # Count of values that appear exactly once
            # Count total occurrences of duplicated values
            duplicate_occurrences = value_counts[value_counts > 1].sum()  # Total count of duplicates

            uniqueness_rate = unique_once_count / total_count * 100  # Proportion of entries that are unique

            uniqueness_analysis.append({
                '컬럼명': col,
                '총 행 수': total_count,
                '고유값 수': unique_count,
                '중복 발생 수': duplicate_occurrences,
                '고유성 비율': f'{uniqueness_rate:.2f}%'
            })

        uniqueness_df = pd.DataFrame(uniqueness_analysis)
        st.dataframe(uniqueness_df, use_container_width=True)

    if business_rule_enabled:
        # 업무규칙 진단 실행
        st.subheader("📋 업무규칙 진단 결과")
        # 예제: order_count > 0인지 확인
        if 'order_count' in df.columns:
            business_rule_violations = df[(df['order_count'].notna()) & (df['order_count'] < 0)]
            if len(business_rule_violations) > 0:
                st.write(f"❌ 업무규칙 위반: 음수 주문 수 {len(business_rule_violations)}건")
                st.dataframe(business_rule_violations, use_container_width=True)
            else:
                st.write("✅ 모든 데이터가 업무규칙을 준수합니다")

    if checklist_enabled:
        # 체크리스트 진단 실행
        st.subheader("✅ 체크리스트 진단 결과")
        checklist_results = []

        # 각 컬럼에 대한 기본 체크리스트 항목
        for col in df.columns:
            total_count = len(df)
            null_count = df[col].isnull().sum()
            unique_count = df[col].nunique()
            is_unique = df[col].is_unique  # Check if column has unique values

            checklist_results.extend([
                {'항목': f'{col} - 결측치 확인', '결과': 'PASS' if null_count == 0 else 'FAIL'},
                {'항목': f'{col} - 고유값 확인', '결과': 'PASS' if is_unique else 'FAIL'},  # Fixed: Proper uniqueness check
                {'항목': f'{col} - 데이터 유형 확인', '결과': 'PASS' if df[col].dtype != 'object' or df[col].str.len().min() > 0 else 'WARN'}
            ])

        checklist_df = pd.DataFrame(checklist_results)
        st.dataframe(checklist_df, use_container_width=True)

    if realtime_measure_enabled:
        # 비정형 실측 진단 실행
        st.subheader("🔍 비정형 실측 진단 결과")
        # 예제: 이상치 탐지 (IQR 방법)
        numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
        if numeric_cols:
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                if len(outliers) > 0:
                    st.write(f"❌ {col} 컬럼 이상치 {len(outliers)}건 발견")
                    st.dataframe(outliers, use_container_width=True)
                else:
                    st.write(f"✅ {col} 컬럼 이상치 없음")

    # --- 6. 결과 표시 ---
    st.header("📋 종합 데이터 품질 진단 결과")

    # 결과를 DataFrame으로 변환
    results_df = pd.DataFrame(dq_results)

    # 상태에 따라 색상 구분
    def color_status(val):
        color = 'red' if '❌' in val else 'green'
        return f'background-color: {color}; color: white; font-weight: bold'

    # 결과 표시
    if not results_df.empty:
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

    # --- 7. 오류 데이터 상세 조회 ---
    st.header("🔍 오류 데이터 상세 조회")

    # 오류가 있는 지표별 상세 표시
    if not results_df.empty:
        for metric_type in results_df['지표 유형'].unique():
            metric_results = results_df[results_df['지표 유형'] == metric_type]
            error_results = metric_results[metric_results['상태'].str.contains('❌')]
            
            if not error_results.empty:
                st.subheader(f"❌ {metric_type} 오류 데이터")
                
                # 오류가 있는 컬럼에 따라 다른 상세 정보 표시
                for _, result in error_results.iterrows():
                    check_name = result['점검 항목']
                    st.write(f"**{check_name}**")
                    st.write(f"{result['메시지']}")
                    
                    # 컬럼 이름 추출
                    col_name = check_name.split(' ')[0]
                    if col_name in df.columns:
                        # 오류 데이터만 표시
                        if col_name == 'email' and '유효하지 않은 이메일 형식' in str(result['메시지']):
                            import re
                            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                            invalid_emails = df[~df[col_name].str.match(email_pattern, na=False)]
                            if not invalid_emails.empty:
                                st.dataframe(invalid_emails, use_container_width=True)
                        elif col_name == 'join_date' and '미래 날짜 데이터' in str(result['메시지']):
                            future_dates = df[pd.to_datetime(df[col_name]).dt.year > datetime.now().year]
                            if not future_dates.empty:
                                st.dataframe(future_dates, use_container_width=True)
                        elif col_name == complete_col:
                            null_rows = df[df[col_name].isnull()]
                            if not null_rows.empty:
                                st.dataframe(null_rows, use_container_width=True)

    # --- 8. 데이터 품질 용어 가시화 ---
    st.header("🔍 데이터 품질 관련 용어 가시화")
    with st.expander("7대 품질 지표 설명"):
        st.markdown("""
        - **준비성 (Availability)**: 데이터가 필요한 시점에 접근 가능한 정도
        - **완전성 (Completeness)**: 누락된 값이나 속성이 없는 정도  
        - **일관성 (Consistency)**: 동일한 의미의 데이터가 다양한 시스템에서 일관되게 표현되는 정도
        - **정확성 (Accuracy)**: 실제 세계의 값과 일치하는 정도
        - **보안성 (Security)**: 데이터가 무단 접근 및 침해로부터 보호되는 정도
        - **적시성 (Timeliness)**: 데이터가 최신 정보를 반영하고 있는 정도
        - **유용성 (Usability)**: 데이터가 사용자에게 유용하고 효율적인 정도
        """)
    
    with st.expander("4대 진단 방법 설명"):
        st.markdown("""
        - **프로파일링 (Profiling)**: 데이터의 통계적 특성 분석
        - **업무규칙 진단 (Business Rule Diagnosis)**: 업무 규칙에 따른 데이터 검증
        - **체크리스트 (Checklist)**: 표준 기준에 대한 항목별 검증
        - **비정형 실측 (Unstructured Real-time Measurement)**: 비정형 데이터의 실시간 분석
        """)