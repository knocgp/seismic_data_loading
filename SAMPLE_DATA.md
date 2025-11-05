# SEGY 샘플 데이터 가이드

이 문서는 SEGY 파일을 GitHub 및 Colab에서 사용하는 다양한 방법을 설명합니다.

## 📦 GitHub에 파일 올리기

### ⚠️ 제약사항
- **일반 업로드**: 최대 100MB
- **Git LFS**: 최대 2GB (무료 계정)
- **저장소 크기**: 권장 1GB 미만

---

## 방법 1: 작은 샘플 파일 (< 100MB)

### GitHub에 직접 업로드

```bash
# 1. 작은 샘플 SEGY 파일 추가
cd /home/user/webapp
mkdir -p sample_data
cp /path/to/small_sample.segy sample_data/

# 2. Git에 추가 및 커밋
git add sample_data/small_sample.segy
git commit -m "Add small sample SEGY file"
git push origin main
```

### Colab에서 사용

```python
# GitHub에서 직접 다운로드
!wget https://github.com/knocgp/seismic_data_loading/raw/main/sample_data/small_sample.segy

# 사용
from header_loading import SEGYHeaderLoader
loader = SEGYHeaderLoader('small_sample.segy')
```

---

## 방법 2: Git LFS 사용 (100MB ~ 2GB)

### 설정 방법

```bash
# 1. Git LFS 설치 (로컬 환경)
# Ubuntu/Debian
sudo apt-get install git-lfs

# macOS
brew install git-lfs

# Windows
# https://git-lfs.github.com/ 에서 다운로드

# 2. Git LFS 초기화
cd /home/user/webapp
git lfs install

# 3. SEGY 파일을 LFS로 추적
git lfs track "*.segy"
git lfs track "*.sgy"
git add .gitattributes

# 4. 파일 추가
git add large_sample.segy
git commit -m "Add large sample SEGY file with LFS"
git push origin main
```

### .gitattributes 파일

```
*.segy filter=lfs diff=lfs merge=lfs -text
*.sgy filter=lfs diff=lfs merge=lfs -text
*.SGY filter=lfs diff=lfs merge=lfs -text
*.SEGY filter=lfs diff=lfs merge=lfs -text
```

### Colab에서 Git LFS 파일 다운로드

```python
# Git LFS 설치
!apt-get install git-lfs
!git lfs install

# 저장소 클론 (LFS 파일 포함)
!git clone https://github.com/knocgp/seismic_data_loading.git
%cd seismic_data_loading

# LFS 파일 가져오기
!git lfs pull

# 사용
segy_file = 'sample_data/large_sample.segy'
```

---

## 방법 3: GitHub Releases (권장 - 대용량 파일)

### 파일 업로드

1. **GitHub 웹에서**:
   - 저장소 페이지 방문
   - "Releases" 클릭
   - "Create a new release" 클릭
   - 태그 생성 (예: `v1.0-data`)
   - 파일 드래그 앤 드롭 (최대 2GB)
   - "Publish release" 클릭

2. **다운로드 URL**:
   ```
   https://github.com/knocgp/seismic_data_loading/releases/download/v1.0-data/sample.segy
   ```

### Colab에서 사용

```python
# Release에서 다운로드
!wget https://github.com/knocgp/seismic_data_loading/releases/download/v1.0-data/sample.segy

# 또는 curl 사용
!curl -L -o sample.segy https://github.com/knocgp/seismic_data_loading/releases/download/v1.0-data/sample.segy

segy_file = 'sample.segy'
```

---

## 방법 4: 외부 호스팅 링크

### 공개 데이터 저장소

```python
# 예제: Open Seismic Data
!wget -O sample.segy "https://example.com/public/data/sample.segy"

# 예제: Google Drive 공유 링크
!pip install gdown -q
!gdown --id FILE_ID -O sample.segy
```

### 추천 무료 호스팅

1. **Google Drive**
   - 15GB 무료
   - 공유 링크 생성 가능
   
2. **Dropbox**
   - 2GB 무료
   - 직접 링크 생성 가능

3. **OneDrive**
   - 5GB 무료
   - 공유 링크 생성 가능

4. **AWS S3** (공개 버킷)
   - 사용량에 따라 과금
   - 직접 URL 접근 가능

---

## 방법 5: 테스트용 미니 샘플 생성

실제 SEGY 구조를 가진 작은 샘플 파일을 생성할 수 있습니다.

### Python 스크립트로 미니 샘플 생성

```python
import segyio
import numpy as np

def create_mini_segy(output_file='mini_sample.segy', 
                     n_traces=50, 
                     n_samples=250):
    """
    테스트용 미니 SEGY 파일 생성
    
    Args:
        output_file: 출력 파일명
        n_traces: 트레이스 수 (기본 50)
        n_samples: 샘플 수 (기본 250)
    """
    # 더미 데이터 생성
    spec = segyio.spec()
    spec.format = 5  # IEEE float
    spec.sorting = 2  # CDP sorted
    spec.samples = range(n_samples)
    spec.ilines = range(n_traces)
    spec.xlines = range(1)
    
    with segyio.create(output_file, spec) as f:
        # 텍스트 헤더
        text = "C01 Mini SEGY sample file for testing                                   "
        text += "C02 Created with Python segyio                                          "
        text += "C03 " + " " * 77
        # 3200바이트까지 채우기
        text = text.ljust(3200)
        f.text[0] = text
        
        # 바이너리 헤더
        f.bin = {
            segyio.BinField.Samples: n_samples,
            segyio.BinField.Interval: 2000,  # 2ms
        }
        
        # 트레이스 데이터
        for i in range(n_traces):
            # 간단한 사인파 + 노이즈
            trace_data = np.sin(np.linspace(0, 10*np.pi, n_samples))
            trace_data += np.random.normal(0, 0.1, n_samples)
            
            f.trace[i] = trace_data
            f.header[i] = {
                segyio.TraceField.TRACE_SEQUENCE_LINE: i + 1,
                segyio.TraceField.TRACE_SEQUENCE_FILE: i + 1,
                segyio.TraceField.CDP: i + 1,
                segyio.TraceField.INLINE_3D: i + 1,
                segyio.TraceField.CROSSLINE_3D: 1,
                segyio.TraceField.TRACE_SAMPLE_COUNT: n_samples,
                segyio.TraceField.TRACE_SAMPLE_INTERVAL: 2000,
            }
    
    print(f"✅ 미니 SEGY 파일 생성: {output_file}")
    print(f"   크기: {os.path.getsize(output_file) / 1024:.2f} KB")
    print(f"   트레이스: {n_traces}, 샘플: {n_samples}")

# 실행
create_mini_segy('mini_sample.segy', n_traces=50, n_samples=250)
```

이 스크립트를 실행하면 약 50KB 크기의 작은 SEGY 파일이 생성됩니다.

---

## 공개 SEGY 데이터 소스

### 무료 샘플 데이터

1. **SEG Wiki**
   - https://wiki.seg.org/wiki/Open_data
   - 다양한 공개 지진 데이터

2. **OpendTect**
   - https://www.dgbes.com/index.php/software#free
   - F3 데모 데이터셋

3. **USGS**
   - https://earthquake.usgs.gov/data/
   - 지진 데이터

4. **Equinor (Volve Dataset)**
   - https://www.equinor.com/energy/volve-data-sharing
   - 대규모 석유 탐사 데이터

---

## 권장 워크플로우

### 소규모 테스트 (< 10MB)
```
로컬 파일 → GitHub 직접 업로드 → Colab에서 wget으로 다운로드
```

### 중규모 파일 (10MB ~ 100MB)
```
로컬 파일 → GitHub 직접 업로드 → Colab에서 wget으로 다운로드
또는
로컬 파일 → GitHub Releases → Colab에서 wget으로 다운로드
```

### 대규모 파일 (100MB ~ 2GB)
```
로컬 파일 → GitHub LFS → Colab에서 git lfs로 다운로드
또는
로컬 파일 → GitHub Releases → Colab에서 wget으로 다운로드
```

### 초대형 파일 (> 2GB)
```
로컬 파일 → Google Drive 업로드 → Colab에서 Drive 마운트
또는
로컬 파일 → 외부 호스팅 → Colab에서 wget/gdown으로 다운로드
```

---

## 실전 예제

### 예제 1: 미니 샘플을 GitHub에 추가

```bash
# 1. 미니 샘플 생성
python -c "
import segyio
import numpy as np
# ... (위의 create_mini_segy 코드)
"

# 2. Git에 추가
git add mini_sample.segy
git commit -m "Add mini sample SEGY file for testing"
git push origin main
```

### 예제 2: Colab에서 사용

```python
# GitHub에서 다운로드
!wget https://github.com/knocgp/seismic_data_loading/raw/main/mini_sample.segy

# 테스트
from header_loading import SEGYHeaderLoader

with SEGYHeaderLoader('mini_sample.segy') as loader:
    loader.print_header_summary()
```

---

## FAQ

### Q: GitHub에 50MB SEGY 파일을 올려도 되나요?
**A**: 네, 100MB 미만이면 직접 업로드 가능합니다. 단, 저장소 크기 제한을 고려하세요.

### Q: Git LFS는 무료인가요?
**A**: GitHub 무료 계정은 매월 1GB 대역폭과 1GB 저장 공간을 제공합니다.

### Q: 가장 좋은 방법은?
**A**: 
- **테스트/데모용**: 미니 샘플을 GitHub에 직접 추가
- **실제 데이터**: Google Drive + Colab 마운트

### Q: 여러 사용자와 공유하려면?
**A**: GitHub Releases 또는 Google Drive 공유 링크 사용

---

## 다음 단계

1. **작은 샘플 추가**: 테스트용 미니 SEGY 파일 생성
2. **문서 업데이트**: README에 샘플 데이터 사용법 추가
3. **Colab 노트북 업데이트**: 샘플 데이터 자동 다운로드 추가

---

## 참고 자료

- [Git LFS](https://git-lfs.github.com/)
- [GitHub 파일 크기 제한](https://docs.github.com/en/repositories/working-with-files/managing-large-files)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
