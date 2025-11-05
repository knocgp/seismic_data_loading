# Google Colab 사용 가이드

Google Colab에서 SEGY 파일을 처리하는 방법을 단계별로 설명합니다.

## 📚 목차
1. [Google Drive에서 파일 사용하기](#1-google-drive에서-파일-사용하기)
2. [로컬 파일 업로드하기](#2-로컬-파일-업로드하기)
3. [GitHub에서 코드 가져오기](#3-github에서-코드-가져오기)
4. [전체 워크플로우](#4-전체-워크플로우)

---

## 1. Google Drive에서 파일 사용하기

### 방법 1-A: Drive 마운트 (권장)

```python
# Google Drive 마운트
from google.colab import drive
drive.mount('/content/drive')

# 마운트 확인
!ls /content/drive/MyDrive/
```

**Drive에 파일 넣는 방법:**
1. 웹 브라우저에서 [Google Drive](https://drive.google.com) 접속
2. 폴더 생성 (예: `SEGY_Data`)
3. SEGY 파일을 드래그 앤 드롭으로 업로드
4. Colab에서 해당 경로 사용

```python
# Drive에 저장된 파일 사용
segy_file = '/content/drive/MyDrive/SEGY_Data/your_file.segy'

# 파일 존재 확인
import os
if os.path.exists(segy_file):
    print(f"✓ 파일 찾음: {segy_file}")
else:
    print(f"✗ 파일 없음: {segy_file}")
```

### 방법 1-B: Drive 파일 직접 선택

```python
# Google Drive 마운트
from google.colab import drive
drive.mount('/content/drive')

# 파일 브라우저로 선택
from google.colab import files
import os

# MyDrive 폴더로 이동
os.chdir('/content/drive/MyDrive')

# 현재 디렉토리의 파일 목록 표시
print("현재 디렉토리의 SEGY 파일:")
!find . -name "*.segy" -o -name "*.sgy" 2>/dev/null | head -20

# 파일 경로 수동 입력
segy_file = input("SEGY 파일 전체 경로를 입력하세요: ")
```

### 로컬 → Google Drive 업로드 방법

#### 방법 A: 웹 인터페이스 (가장 쉬움)
1. 브라우저에서 [drive.google.com](https://drive.google.com) 열기
2. 왼쪽 상단 "새로 만들기" 클릭
3. "파일 업로드" 선택
4. 로컬 SEGY 파일 선택
5. 업로드 완료 대기

#### 방법 B: Google Drive 데스크톱 앱
1. [Google Drive 데스크톱](https://www.google.com/drive/download/) 설치
2. 로그인 후 동기화 폴더 설정
3. 로컬 SEGY 파일을 Google Drive 폴더에 복사
4. 자동 동기화 대기

#### 방법 C: Google Drive API (대용량 파일)
```bash
# 로컬 터미널에서 실행
# rclone 설치 (https://rclone.org/)
rclone copy /path/to/local/file.segy gdrive:SEGY_Data/
```

---

## 2. 로컬 파일 업로드하기

### 방법 2-A: 파일 업로드 위젯 (간단한 파일)

```python
from google.colab import files
import os

# 파일 업로드
print("SEGY 파일을 선택하세요...")
uploaded = files.upload()

# 업로드된 파일 확인
segy_file = list(uploaded.keys())[0]
print(f"\n업로드된 파일: {segy_file}")
print(f"파일 크기: {os.path.getsize(segy_file) / (1024*1024):.2f} MB")
```

**⚠️ 주의사항:**
- 세션이 종료되면 파일이 삭제됨
- 대용량 파일(>100MB)은 업로드 시간이 오래 걸림
- 네트워크 끊김 시 재업로드 필요

### 방법 2-B: wget으로 다운로드

```python
# 공개 URL에서 다운로드
!wget -O sample.segy "https://example.com/path/to/file.segy"

segy_file = "sample.segy"
```

### 방법 2-C: gdown으로 Google Drive 공유 링크 다운로드

```python
# gdown 설치
!pip install gdown -q

# Google Drive 공유 링크에서 다운로드
# 1. Drive에서 파일 우클릭 → "링크 가져오기"
# 2. "링크가 있는 모든 사용자" 로 설정
# 3. 링크 복사 (예: https://drive.google.com/file/d/FILE_ID/view?usp=sharing)

import gdown

# FILE_ID 부분만 추출하여 사용
file_id = "YOUR_FILE_ID"
url = f"https://drive.google.com/uc?id={file_id}"
output = "downloaded.segy"

gdown.download(url, output, quiet=False)
segy_file = output
```

---

## 3. GitHub에서 코드 가져오기

### 방법 3-A: 저장소 클론

```python
# 저장소 클론
!git clone https://github.com/knocgp/seismic_data_loading.git
%cd seismic_data_loading

# 필요한 라이브러리 설치
!pip install -r requirements.txt -q

# 모듈 import
from header_loading import SEGYHeaderLoader
from data_loading import SEGYDataLoader
from data_divide import SEGYDataDivider
```

### 방법 3-B: 파일 직접 다운로드

```python
# 개별 파일 다운로드
!wget https://raw.githubusercontent.com/knocgp/seismic_data_loading/main/header_loading.py
!wget https://raw.githubusercontent.com/knocgp/seismic_data_loading/main/data_loading.py
!wget https://raw.githubusercontent.com/knocgp/seismic_data_loading/main/data_divide.py
!wget https://raw.githubusercontent.com/knocgp/seismic_data_loading/main/requirements.txt

# 라이브러리 설치
!pip install -r requirements.txt -q

# 모듈 import
from header_loading import SEGYHeaderLoader
from data_loading import SEGYDataLoader
from data_divide import SEGYDataDivider
```

---

## 4. 전체 워크플로우

### 🎯 워크플로우 1: Drive 사용 (권장)

```python
# ============================================
# Step 1: 환경 설정
# ============================================
# 라이브러리 설치
!pip install segyio numpy matplotlib -q

# Google Drive 마운트
from google.colab import drive
drive.mount('/content/drive')

# ============================================
# Step 2: 코드 가져오기
# ============================================
# GitHub에서 클론
!git clone https://github.com/knocgp/seismic_data_loading.git
%cd seismic_data_loading

# 모듈 import
from header_loading import SEGYHeaderLoader
from data_loading import SEGYDataLoader
from data_divide import SEGYDataDivider
import matplotlib.pyplot as plt
import numpy as np

# ============================================
# Step 3: SEGY 파일 경로 설정
# ============================================
# Drive에 저장된 파일 사용
segy_file = '/content/drive/MyDrive/SEGY_Data/your_file.segy'

# 파일 존재 확인
import os
if not os.path.exists(segy_file):
    print(f"❌ 파일을 찾을 수 없습니다: {segy_file}")
    print("\n사용 가능한 SEGY 파일:")
    !find /content/drive/MyDrive -name "*.segy" -o -name "*.sgy" 2>/dev/null | head -10
else:
    print(f"✅ 파일 찾음: {segy_file}")

# ============================================
# Step 4: 헤더 분석
# ============================================
with SEGYHeaderLoader(segy_file) as loader:
    loader.print_header_summary()
    info = loader.get_file_info()

# ============================================
# Step 5: 데이터 로드 및 시각화
# ============================================
with SEGYDataLoader(segy_file) as loader:
    # 처음 100개 트레이스 로드
    data = loader.load_traces(0, 100)
    time_axis = loader.get_time_axis()
    
    # 시각화
    plt.figure(figsize=(12, 6))
    plt.imshow(data.T, aspect='auto', cmap='seismic',
               extent=[0, 100, time_axis[-1], time_axis[0]],
               vmin=-np.percentile(np.abs(data), 95),
               vmax=np.percentile(np.abs(data), 95))
    plt.colorbar(label='Amplitude')
    plt.xlabel('Trace Number')
    plt.ylabel('Time/Depth (ms)')
    plt.title('SEGY Data Preview')
    plt.show()

# ============================================
# Step 6: 데이터 분할 (옵션)
# ============================================
with SEGYDataDivider(segy_file) as divider:
    chunks = divider.divide_by_grid(100, 500.0)
    divider.print_division_info(chunks)
    
    # Drive에 저장
    output_dir = '/content/drive/MyDrive/SEGY_Chunks'
    divider.save_all_chunks(chunks, output_dir)

print("✅ 처리 완료!")
```

### 🎯 워크플로우 2: 파일 업로드 방식

```python
# ============================================
# Step 1: 환경 설정
# ============================================
!pip install segyio numpy matplotlib -q

# GitHub에서 코드 가져오기
!git clone https://github.com/knocgp/seismic_data_loading.git
%cd seismic_data_loading

from header_loading import SEGYHeaderLoader
from data_loading import SEGYDataLoader
import matplotlib.pyplot as plt
import numpy as np

# ============================================
# Step 2: SEGY 파일 업로드
# ============================================
from google.colab import files
print("SEGY 파일을 업로드하세요...")
uploaded = files.upload()
segy_file = list(uploaded.keys())[0]
print(f"✅ 업로드 완료: {segy_file}")

# ============================================
# Step 3: 데이터 처리
# ============================================
# 헤더 분석
with SEGYHeaderLoader(segy_file) as loader:
    loader.print_header_summary()

# 데이터 로드 및 시각화
with SEGYDataLoader(segy_file) as loader:
    data = loader.load_traces(0, 100)
    time_axis = loader.get_time_axis()
    
    plt.figure(figsize=(12, 6))
    plt.imshow(data.T, aspect='auto', cmap='seismic',
               extent=[0, 100, time_axis[-1], time_axis[0]])
    plt.colorbar(label='Amplitude')
    plt.xlabel('Trace Number')
    plt.ylabel('Time/Depth (ms)')
    plt.show()

print("✅ 처리 완료!")
```

---

## 5. 실전 팁

### 💡 Tip 1: 파일 크기 확인

```python
import os

def get_file_size(filepath):
    size_bytes = os.path.getsize(filepath)
    size_mb = size_bytes / (1024 * 1024)
    size_gb = size_bytes / (1024 * 1024 * 1024)
    
    if size_gb >= 1:
        return f"{size_gb:.2f} GB"
    else:
        return f"{size_mb:.2f} MB"

print(f"파일 크기: {get_file_size(segy_file)}")
```

### 💡 Tip 2: Drive 공간 확인

```python
# Drive 마운트 후
!df -h /content/drive

# 특정 폴더 크기 확인
!du -sh /content/drive/MyDrive/SEGY_Data
```

### 💡 Tip 3: 처리 결과를 Drive에 자동 저장

```python
from datetime import datetime

# 타임스탬프로 폴더 생성
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = f'/content/drive/MyDrive/SEGY_Results/{timestamp}'

# 결과 저장
with SEGYDataDivider(segy_file) as divider:
    chunks = divider.divide_by_grid(100, 500.0)
    divider.save_all_chunks(chunks, output_dir)

print(f"✅ 결과 저장: {output_dir}")
```

### 💡 Tip 4: 대용량 파일 처리

```python
# 메모리 사용량 확인
import psutil
import os

def print_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    print(f"메모리 사용: {mem_info.rss / (1024**3):.2f} GB")

print_memory_usage()

# 대용량 파일은 청크 단위로 처리
with SEGYDataLoader(segy_file) as loader:
    # 전체가 아닌 일부만 로드
    chunk_size = 1000
    for i in range(0, loader.total_traces, chunk_size):
        end = min(i + chunk_size, loader.total_traces)
        data = loader.load_traces(i, end)
        # 처리 로직
        print(f"Processed traces {i}-{end}")
        print_memory_usage()
```

### 💡 Tip 5: 세션 타임아웃 방지

```python
# 주기적으로 실행할 코드 (JavaScript)
from IPython.display import display, Javascript

display(Javascript('''
function KeepAlive() {
    console.log("Keep alive ping");
    setTimeout(KeepAlive, 60000); // 1분마다 실행
}
KeepAlive();
'''))
```

---

## 6. 문제 해결

### ❌ "파일을 찾을 수 없습니다"

```python
# Drive가 마운트되었는지 확인
import os
if os.path.exists('/content/drive/MyDrive'):
    print("✓ Drive 마운트됨")
else:
    print("✗ Drive 마운트 필요")
    from google.colab import drive
    drive.mount('/content/drive')

# 파일 경로 확인
!ls -lh /content/drive/MyDrive/SEGY_Data/
```

### ❌ "메모리 부족" 오류

```python
# 1. 런타임 재시작
# 2. 부분 로드 사용
with SEGYDataLoader(segy_file) as loader:
    # 전체 대신 일부만 로드
    data = loader.load_traces(0, 100)  # 처음 100개만
```

### ❌ "ModuleNotFoundError"

```python
# 라이브러리 재설치
!pip install --force-reinstall segyio numpy matplotlib
```

---

## 7. 유용한 단축키

| 단축키 | 기능 |
|--------|------|
| `Ctrl + Enter` | 현재 셀 실행 |
| `Shift + Enter` | 현재 셀 실행 후 다음 셀로 이동 |
| `Ctrl + M B` | 아래에 새 셀 추가 |
| `Ctrl + M A` | 위에 새 셀 추가 |
| `Ctrl + M D` | 셀 삭제 |
| `Ctrl + /` | 주석 토글 |

---

## 8. 추가 리소스

- [Google Colab 공식 문서](https://colab.research.google.com/notebooks/intro.ipynb)
- [Google Drive API](https://developers.google.com/drive)
- [segyio 문서](https://segyio.readthedocs.io/)
- [GitHub 저장소](https://github.com/knocgp/seismic_data_loading)

---

## 문의사항

문제가 있거나 질문이 있으시면 GitHub Issues에 등록해주세요:
https://github.com/knocgp/seismic_data_loading/issues
