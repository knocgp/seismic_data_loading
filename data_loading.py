"""
SEGY Data Loading Module
SEG-Y 파일의 실제 지진 데이터를 로드하는 모듈
"""

import segyio
import numpy as np
from typing import Optional, Tuple, List
import warnings


class SEGYDataLoader:
    """SEG-Y 데이터를 로드하고 처리하는 클래스"""
    
    def __init__(self, filepath: str):
        """
        SEGYDataLoader 초기화
        
        Args:
            filepath: SEGY 파일 경로
        """
        self.filepath = filepath
        self.file = None
        self._total_traces = None
        self._samples_per_trace = None
        self._sample_interval = None
        
    def __enter__(self):
        """Context manager 진입"""
        self.file = segyio.open(self.filepath, ignore_geometry=True)
        self._total_traces = len(self.file.trace)
        self._samples_per_trace = self.file.bin[segyio.BinField.Samples]
        self._sample_interval = self.file.bin[segyio.BinField.Interval] / 1000  # ms
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        if self.file:
            self.file.close()
    
    @property
    def total_traces(self) -> int:
        """총 트레이스 수 반환"""
        if self._total_traces is None:
            raise ValueError("파일이 열리지 않았습니다.")
        return self._total_traces
    
    @property
    def samples_per_trace(self) -> int:
        """트레이스당 샘플 수 반환"""
        if self._samples_per_trace is None:
            raise ValueError("파일이 열리지 않았습니다.")
        return self._samples_per_trace
    
    @property
    def sample_interval(self) -> float:
        """샘플 간격 (ms) 반환"""
        if self._sample_interval is None:
            raise ValueError("파일이 열리지 않았습니다.")
        return self._sample_interval
    
    def load_trace(self, trace_index: int) -> np.ndarray:
        """
        단일 트레이스 데이터 로드
        
        Args:
            trace_index: 트레이스 인덱스 (0부터 시작)
            
        Returns:
            1D numpy 배열 (samples_per_trace,)
        """
        if not self.file:
            raise ValueError("파일이 열리지 않았습니다.")
        
        if trace_index < 0 or trace_index >= self.total_traces:
            raise ValueError(f"트레이스 인덱스가 범위를 벗어났습니다. (0 ~ {self.total_traces - 1})")
        
        return self.file.trace[trace_index]
    
    def load_traces(self, start_trace: int = 0, end_trace: Optional[int] = None) -> np.ndarray:
        """
        여러 트레이스 데이터 로드
        
        Args:
            start_trace: 시작 트레이스 인덱스
            end_trace: 종료 트레이스 인덱스 (None이면 끝까지)
            
        Returns:
            2D numpy 배열 (num_traces, samples_per_trace)
        """
        if not self.file:
            raise ValueError("파일이 열리지 않았습니다.")
        
        if end_trace is None:
            end_trace = self.total_traces
        
        if start_trace < 0 or start_trace >= self.total_traces:
            raise ValueError(f"시작 트레이스 인덱스가 범위를 벗어났습니다.")
        
        if end_trace <= start_trace or end_trace > self.total_traces:
            raise ValueError(f"종료 트레이스 인덱스가 올바르지 않습니다.")
        
        num_traces = end_trace - start_trace
        data = np.zeros((num_traces, self.samples_per_trace), dtype=np.float32)
        
        for i, trace_idx in enumerate(range(start_trace, end_trace)):
            data[i] = self.file.trace[trace_idx]
        
        return data
    
    def load_all_data(self) -> np.ndarray:
        """
        전체 데이터 로드
        
        Returns:
            2D numpy 배열 (total_traces, samples_per_trace)
        """
        if not self.file:
            raise ValueError("파일이 열리지 않았습니다.")
        
        # 메모리 경고
        total_size_mb = (self.total_traces * self.samples_per_trace * 4) / (1024 * 1024)
        if total_size_mb > 1000:  # 1GB 이상
            warnings.warn(f"전체 데이터 크기가 {total_size_mb:.2f} MB로 매우 큽니다. "
                         "메모리 부족 문제가 발생할 수 있습니다.")
        
        return self.load_traces(0, self.total_traces)
    
    def load_depth_slice(self, start_sample: int = 0, end_sample: Optional[int] = None,
                         start_trace: int = 0, end_trace: Optional[int] = None) -> np.ndarray:
        """
        특정 깊이/시간 범위의 데이터 로드
        
        Args:
            start_sample: 시작 샘플 인덱스 (depth/time 방향)
            end_sample: 종료 샘플 인덱스 (None이면 끝까지)
            start_trace: 시작 트레이스 인덱스
            end_trace: 종료 트레이스 인덱스 (None이면 끝까지)
            
        Returns:
            2D numpy 배열 (num_traces, num_samples)
        """
        if end_sample is None:
            end_sample = self.samples_per_trace
        
        if end_trace is None:
            end_trace = self.total_traces
        
        if start_sample < 0 or start_sample >= self.samples_per_trace:
            raise ValueError(f"시작 샘플 인덱스가 범위를 벗어났습니다.")
        
        if end_sample <= start_sample or end_sample > self.samples_per_trace:
            raise ValueError(f"종료 샘플 인덱스가 올바르지 않습니다.")
        
        # 전체 트레이스 로드 후 깊이/시간 슬라이싱
        data = self.load_traces(start_trace, end_trace)
        return data[:, start_sample:end_sample]
    
    def get_time_axis(self, start_sample: int = 0, end_sample: Optional[int] = None) -> np.ndarray:
        """
        시간/깊이 축 생성
        
        Args:
            start_sample: 시작 샘플 인덱스
            end_sample: 종료 샘플 인덱스 (None이면 끝까지)
            
        Returns:
            시간/깊이 값 배열 (ms 또는 m)
        """
        if end_sample is None:
            end_sample = self.samples_per_trace
        
        num_samples = end_sample - start_sample
        time_axis = np.arange(num_samples) * self.sample_interval + (start_sample * self.sample_interval)
        return time_axis
    
    def get_trace_axis(self, start_trace: int = 0, end_trace: Optional[int] = None) -> np.ndarray:
        """
        트레이스 축 생성
        
        Args:
            start_trace: 시작 트레이스 인덱스
            end_trace: 종료 트레이스 인덱스 (None이면 끝까지)
            
        Returns:
            트레이스 번호 배열
        """
        if end_trace is None:
            end_trace = self.total_traces
        
        return np.arange(start_trace, end_trace)
    
    def get_data_statistics(self, data: Optional[np.ndarray] = None) -> dict:
        """
        데이터 통계 정보 계산
        
        Args:
            data: 분석할 데이터 (None이면 전체 데이터 로드)
            
        Returns:
            통계 정보 딕셔너리
        """
        if data is None:
            # 전체 데이터 로드는 메모리 문제가 있을 수 있으므로 샘플링
            if self.total_traces > 1000:
                warnings.warn("전체 데이터가 크므로 1000개 트레이스를 샘플링하여 통계를 계산합니다.")
                step = self.total_traces // 1000
                data = self.load_traces(0, self.total_traces)[::step]
            else:
                data = self.load_all_data()
        
        stats = {
            'shape': data.shape,
            'dtype': str(data.dtype),
            'min': float(np.min(data)),
            'max': float(np.max(data)),
            'mean': float(np.mean(data)),
            'std': float(np.std(data)),
            'median': float(np.median(data)),
            'percentile_95': float(np.percentile(data, 95)),
            'percentile_5': float(np.percentile(data, 5)),
        }
        
        return stats
    
    def print_data_info(self, include_stats: bool = False):
        """데이터 정보 출력"""
        print("=" * 60)
        print("SEGY DATA INFORMATION")
        print("=" * 60)
        print(f"파일 경로: {self.filepath}")
        print(f"\n[데이터 형태]")
        print(f"  총 트레이스 수: {self.total_traces:,}")
        print(f"  트레이스당 샘플 수: {self.samples_per_trace:,}")
        print(f"  데이터 형태: ({self.total_traces}, {self.samples_per_trace})")
        print(f"\n[시간/깊이 정보]")
        print(f"  샘플 간격: {self.sample_interval:.3f} ms")
        print(f"  총 시간/깊이: {self.sample_interval * self.samples_per_trace:.3f} ms")
        
        if include_stats:
            print(f"\n[데이터 통계]")
            stats = self.get_data_statistics()
            print(f"  최소값: {stats['min']:.6e}")
            print(f"  최대값: {stats['max']:.6e}")
            print(f"  평균: {stats['mean']:.6e}")
            print(f"  표준편차: {stats['std']:.6e}")
            print(f"  중앙값: {stats['median']:.6e}")
        
        print("=" * 60)


def load_segy_data(filepath: str, start_trace: int = 0, end_trace: Optional[int] = None,
                   start_sample: int = 0, end_sample: Optional[int] = None) -> Tuple[np.ndarray, dict]:
    """
    SEGY 파일에서 데이터를 간단하게 로드하는 함수
    
    Args:
        filepath: SEGY 파일 경로
        start_trace: 시작 트레이스 인덱스
        end_trace: 종료 트레이스 인덱스 (None이면 끝까지)
        start_sample: 시작 샘플 인덱스
        end_sample: 종료 샘플 인덱스 (None이면 끝까지)
        
    Returns:
        (데이터 배열, 메타데이터 딕셔너리)
    """
    with SEGYDataLoader(filepath) as loader:
        data = loader.load_depth_slice(start_sample, end_sample, start_trace, end_trace)
        
        metadata = {
            'total_traces': loader.total_traces,
            'samples_per_trace': loader.samples_per_trace,
            'sample_interval': loader.sample_interval,
            'loaded_traces': (start_trace, end_trace if end_trace else loader.total_traces),
            'loaded_samples': (start_sample, end_sample if end_sample else loader.samples_per_trace),
            'time_axis': loader.get_time_axis(start_sample, end_sample),
            'trace_axis': loader.get_trace_axis(start_trace, end_trace),
        }
        
        return data, metadata


if __name__ == "__main__":
    # 사용 예제
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        print(f"SEGY 데이터 로드: {filepath}\n")
        
        with SEGYDataLoader(filepath) as loader:
            loader.print_data_info(include_stats=True)
            
            # 첫 10개 트레이스 로드
            print("\n첫 10개 트레이스 로드 중...")
            data = loader.load_traces(0, 10)
            print(f"로드된 데이터 형태: {data.shape}")
            print(f"데이터 타입: {data.dtype}")
    else:
        print("사용법: python data_loading.py <segy_file_path>")
