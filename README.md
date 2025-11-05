# SEGY File Processing Tools

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/knocgp/seismic_data_loading/blob/main/quickstart_colab.ipynb)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/knocgp/seismic_data_loading)
[![Python](https://img.shields.io/badge/Python-3.7+-blue?logo=python)](https://www.python.org/)

SEG-Y 형식의 지진 데이터를 로드, 분석, 분할, 시각화하는 Python 도구 모음입니다.

## 🚀 빠른 시작

### Google Colab에서 바로 사용하기 (권장)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/knocgp/seismic_data_loading/blob/main/quickstart_colab.ipynb)

위 버튼을 클릭하면 **설치 없이** 바로 사용할 수 있습니다!

- ✅ 환경 설정 자동화
- ✅ Google Drive 연동
- ✅ 단계별 가이드
- ✅ 즉시 시각화

### 튜토리얼 노트북

- **빠른 시작**: [`quickstart_colab.ipynb`](https://colab.research.google.com/github/knocgp/seismic_data_loading/blob/main/quickstart_colab.ipynb) - Colab에서 바로 실행
- **전체 튜토리얼**: [`segy_processing_tutorial.ipynb`](https://colab.research.google.com/github/knocgp/seismic_data_loading/blob/main/segy_processing_tutorial.ipynb) - 상세한 예제 포함
- **Colab 가이드**: [`COLAB_GUIDE.md`](COLAB_GUIDE.md) - Drive 연동 및 사용법

## 주요 기능

- 📖 **헤더 분석**: Textual, Binary, Trace 헤더 정보 추출 및 분석
- 📊 **데이터 로드**: 전체 또는 부분 지진 데이터 로드
- ✂️ **데이터 분할**: 트레이스 및 깊이/시간 기준 데이터 분할
- 📈 **시각화**: 다양한 형태의 데이터 시각화
- 💾 **데이터 저장**: 분할된 청크를 NumPy 파일로 저장

## 설치

### 1. 필요한 라이브러리 설치

```bash
pip install -r requirements.txt
```

또는 개별 설치:

```bash
pip install segyio numpy matplotlib
```

### 2. 모듈 다운로드

다음 파일들을 같은 디렉토리에 저장하세요:
- `header_loading.py` - 헤더 정보 로드
- `data_loading.py` - 데이터 로드
- `data_divide.py` - 데이터 분할
- `segy_processing_tutorial.ipynb` - Jupyter 노트북 튜토리얼

## 사용 방법

### 1. Python 스크립트로 사용

#### 헤더 정보 확인

```python
from header_loading import SEGYHeaderLoader

with SEGYHeaderLoader('your_file.segy') as loader:
    # 전체 요약 출력
    loader.print_header_summary()
    
    # 파일 정보 가져오기
    info = loader.get_file_info()
    print(f"총 트레이스 수: {info['total_traces']}")
    print(f"샘플 간격: {info['sample_interval_ms']} ms")
```

#### 데이터 로드

```python
from data_loading import SEGYDataLoader

with SEGYDataLoader('your_file.segy') as loader:
    # 처음 100개 트레이스 로드
    data = loader.load_traces(0, 100)
    print(f"데이터 형태: {data.shape}")
    
    # 시간/깊이 축 생성
    time_axis = loader.get_time_axis()
```

#### 데이터 분할

```python
from data_divide import SEGYDataDivider

with SEGYDataDivider('your_file.segy') as divider:
    # 트레이스 100개, 깊이 500ms 간격으로 분할
    chunks = divider.divide_by_grid(
        num_traces_per_chunk=100,
        depth_interval_ms=500.0
    )
    
    # 분할 정보 출력
    divider.print_division_info(chunks)
    
    # 청크 저장
    divider.save_all_chunks(chunks, output_dir='./chunks')
```

#### 간편 사용 함수

```python
from header_loading import load_segy_header
from data_loading import load_segy_data
from data_divide import divide_segy_file

# 헤더 정보
info = load_segy_header('your_file.segy', verbose=True)

# 데이터 로드
data, metadata = load_segy_data(
    'your_file.segy',
    start_trace=0,
    end_trace=100,
    start_sample=0,
    end_sample=500
)

# 데이터 분할
chunks = divide_segy_file(
    'your_file.segy',
    num_traces_per_chunk=100,
    depth_interval_ms=500.0,
    output_dir='./chunks',
    save_chunks=True
)
```

### 2. 명령줄에서 사용

#### 헤더 분석

```bash
python header_loading.py your_file.segy
```

#### 데이터 정보 확인

```bash
python data_loading.py your_file.segy
```

#### 데이터 분할

```bash
python data_divide.py your_file.segy 100 500
# 트레이스 100개, 깊이/시간 500ms 간격으로 분할
```

### 3. Google Colab에서 사용

1. `segy_processing_tutorial.ipynb` 파일을 Google Colab에 업로드
2. 필요한 Python 모듈 파일들 업로드:
   - `header_loading.py`
   - `data_loading.py`
   - `data_divide.py`
3. SEGY 파일 업로드
4. 노트북 셀을 순서대로 실행

#### Colab 빠른 시작

```python
# 1. 라이브러리 설치
!pip install segyio numpy matplotlib -q

# 2. 파일 업로드
from google.colab import files
uploaded = files.upload()

# 3. 모듈 import
from header_loading import SEGYHeaderLoader
from data_loading import SEGYDataLoader
from data_divide import SEGYDataDivider

# 4. 사용
segy_file = list(uploaded.keys())[0]
with SEGYHeaderLoader(segy_file) as loader:
    loader.print_header_summary()
```

## 주요 클래스 및 함수

### header_loading.py

#### `SEGYHeaderLoader`
- `load_textual_header()`: Textual Header 로드
- `load_binary_header()`: Binary Header 로드
- `load_trace_header(trace_index)`: Trace Header 로드
- `get_file_info()`: 전체 파일 정보 가져오기
- `print_header_summary()`: 헤더 요약 출력

#### `load_segy_header(filepath, verbose=True)`
간편하게 헤더 정보를 로드하는 함수

### data_loading.py

#### `SEGYDataLoader`
- `load_trace(trace_index)`: 단일 트레이스 로드
- `load_traces(start_trace, end_trace)`: 여러 트레이스 로드
- `load_all_data()`: 전체 데이터 로드
- `load_depth_slice(...)`: 특정 깊이/시간 범위 로드
- `get_time_axis()`: 시간/깊이 축 생성
- `get_data_statistics()`: 데이터 통계 계산

#### `load_segy_data(filepath, start_trace, end_trace, start_sample, end_sample)`
간편하게 데이터를 로드하는 함수

### data_divide.py

#### `SEGYDataDivider`
- `divide_by_traces(num_traces_per_chunk)`: 트레이스 개수로 분할
- `divide_by_depth(depth_interval_ms)`: 깊이/시간 간격으로 분할
- `divide_by_grid(...)`: 그리드 형태로 분할
- `extract_chunk(trace_range, sample_range)`: 청크 추출
- `save_chunk_as_npy(...)`: 청크를 NumPy 파일로 저장
- `save_all_chunks(...)`: 모든 청크 저장

#### `divide_segy_file(filepath, num_traces_per_chunk, depth_interval_ms, ...)`
간편하게 파일을 분할하는 함수

## 시각화 예제

### 기본 시각화

```python
import matplotlib.pyplot as plt
from data_loading import SEGYDataLoader

with SEGYDataLoader('your_file.segy') as loader:
    # 데이터 로드
    data = loader.load_traces(0, 100)
    time_axis = loader.get_time_axis()
    
    # 시각화
    plt.figure(figsize=(12, 6))
    plt.imshow(data.T, aspect='auto', cmap='seismic',
               extent=[0, 100, time_axis[-1], time_axis[0]])
    plt.colorbar(label='Amplitude')
    plt.xlabel('Trace Number')
    plt.ylabel('Time/Depth (ms)')
    plt.title('SEGY Data')
    plt.show()
```

### 단일 트레이스 시각화

```python
with SEGYDataLoader('your_file.segy') as loader:
    trace_data = loader.load_trace(50)
    time_axis = loader.get_time_axis()
    
    plt.figure(figsize=(6, 8))
    plt.plot(trace_data, time_axis)
    plt.xlabel('Amplitude')
    plt.ylabel('Time/Depth (ms)')
    plt.title('Trace #50')
    plt.gca().invert_yaxis()
    plt.grid(True)
    plt.show()
```

## 데이터 형식

### 입력
- **SEGY/SGY 파일**: SEG-Y Rev 0, Rev 1, Rev 2 형식 지원

### 출력
- **NumPy 파일 (.npy)**: 각 청크의 데이터
- **JSON 파일 (.json)**: 각 청크의 메타데이터

### 청크 메타데이터 예제

```json
{
  "chunk_id": [0, 0],
  "chunk_number": 0,
  "trace_range": [0, 100],
  "sample_range": [0, 250],
  "time_range_ms": [0.0, 500.0],
  "shape": [100, 250],
  "source_file": "your_file.segy"
}
```

## 성능 고려사항

### 메모리 사용
- 전체 데이터 로드 시 메모리 사용량이 클 수 있습니다
- 대용량 파일의 경우 부분 로드 또는 청크 단위 처리를 권장합니다
- 예: 1000 traces × 5000 samples × 4 bytes = 약 20MB

### 처리 속도
- 청크 크기가 작을수록 청크 개수가 많아져 저장 시간이 증가합니다
- 권장 청크 크기: 100~500 traces, 500~1000ms 간격

### 최적화 팁
1. 필요한 범위만 로드
2. 통계 계산 시 샘플링 사용
3. 청크 크기를 적절히 조정
4. NumPy 파일로 저장하여 재사용

## 예제 데이터

### 포함된 샘플 파일

이 저장소에는 테스트용 미니 SEGY 샘플이 포함되어 있습니다:

- **mini_sample.segy** (65KB) - 50 트레이스 × 250 샘플
  - 합성 지진 데이터 (사인파 + 노이즈)
  - 테스트 및 학습용

샘플 파일 사용:
```python
# GitHub에서 직접 다운로드
!wget https://github.com/knocgp/seismic_data_loading/raw/main/mini_sample.segy

# 또는 저장소 클론 후 사용
from header_loading import SEGYHeaderLoader
loader = SEGYHeaderLoader('mini_sample.segy')
```

### 추가 샘플 생성

```bash
# 다양한 크기의 샘플 생성
python create_sample_segy.py --multiple

# 커스텀 샘플 생성
python create_sample_segy.py my_sample.segy 100 500
```

### 공개 SEGY 데이터

실제 지진 데이터가 필요하다면 다음 소스를 참고하세요:

- [SEG Wiki](https://wiki.seg.org/wiki/Open_data)
- [Open Seismic Repository](https://opendtect.org/osr/)
- [USGS Data](https://www.usgs.gov/)
- [Equinor Volve Dataset](https://www.equinor.com/energy/volve-data-sharing)

## 문제 해결

### segyio 설치 오류
```bash
# Windows의 경우
pip install segyio --no-cache-dir

# Linux/Mac의 경우
pip install segyio
```

### 메모리 부족 오류
- 전체 데이터 로드 대신 부분 로드 사용
- 청크 크기를 줄임
- 샘플링을 통한 통계 계산

### 파일 형식 오류
- SEGY 파일이 표준 형식인지 확인
- `ignore_geometry=True` 옵션 사용

## 라이선스

MIT License

## 기여

버그 리포트, 기능 요청, 풀 리퀘스트를 환영합니다!

## 참고 자료

- [SEG-Y Format Specification](https://seg.org/Portals/0/SEG/News%20and%20Resources/Technical%20Standards/seg_y_rev2_0-mar2017.pdf)
- [segyio Documentation](https://segyio.readthedocs.io/)
- [NumPy Documentation](https://numpy.org/doc/)
- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)

## 연락처

문제가 있거나 질문이 있으시면 이슈를 등록해주세요.
