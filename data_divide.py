"""
SEGY Data Divide Module
SEG-Y 데이터를 분할하고 저장하는 모듈
"""

import segyio
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
from pathlib import Path
import os
from header_loading import SEGYHeaderLoader
from data_loading import SEGYDataLoader


class SEGYDataDivider:
    """SEG-Y 데이터를 분할하는 클래스"""
    
    def __init__(self, filepath: str):
        """
        SEGYDataDivider 초기화
        
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
        return self._total_traces
    
    @property
    def samples_per_trace(self) -> int:
        """트레이스당 샘플 수 반환"""
        return self._samples_per_trace
    
    @property
    def sample_interval(self) -> float:
        """샘플 간격 (ms) 반환"""
        return self._sample_interval
    
    def divide_by_traces(self, num_traces_per_chunk: int) -> List[Tuple[int, int]]:
        """
        트레이스 개수로 데이터 분할
        
        Args:
            num_traces_per_chunk: 청크당 트레이스 수
            
        Returns:
            [(시작_트레이스, 종료_트레이스), ...] 리스트
        """
        if num_traces_per_chunk <= 0:
            raise ValueError("청크당 트레이스 수는 양수여야 합니다.")
        
        chunks = []
        for start in range(0, self.total_traces, num_traces_per_chunk):
            end = min(start + num_traces_per_chunk, self.total_traces)
            chunks.append((start, end))
        
        return chunks
    
    def divide_by_depth(self, depth_interval_ms: float) -> List[Tuple[int, int]]:
        """
        깊이/시간 간격으로 데이터 분할
        
        Args:
            depth_interval_ms: 분할 간격 (ms 또는 m)
            
        Returns:
            [(시작_샘플, 종료_샘플), ...] 리스트
        """
        if depth_interval_ms <= 0:
            raise ValueError("깊이 간격은 양수여야 합니다.")
        
        # 샘플 간격으로 변환
        samples_per_chunk = int(depth_interval_ms / self.sample_interval)
        if samples_per_chunk == 0:
            samples_per_chunk = 1
        
        chunks = []
        for start in range(0, self.samples_per_trace, samples_per_chunk):
            end = min(start + samples_per_chunk, self.samples_per_trace)
            chunks.append((start, end))
        
        return chunks
    
    def divide_by_grid(self, num_traces_per_chunk: int, 
                       depth_interval_ms: float) -> List[Dict[str, Any]]:
        """
        트레이스와 깊이/시간을 모두 고려하여 그리드 분할
        
        Args:
            num_traces_per_chunk: 청크당 트레이스 수
            depth_interval_ms: 깊이/시간 분할 간격 (ms)
            
        Returns:
            [{
                'chunk_id': (trace_chunk_idx, depth_chunk_idx),
                'trace_range': (start, end),
                'sample_range': (start, end),
                'time_range_ms': (start, end)
            }, ...] 리스트
        """
        trace_chunks = self.divide_by_traces(num_traces_per_chunk)
        depth_chunks = self.divide_by_depth(depth_interval_ms)
        
        grid_chunks = []
        chunk_id = 0
        
        for t_idx, (t_start, t_end) in enumerate(trace_chunks):
            for d_idx, (d_start, d_end) in enumerate(depth_chunks):
                time_start = d_start * self.sample_interval
                time_end = d_end * self.sample_interval
                
                grid_chunks.append({
                    'chunk_id': (t_idx, d_idx),
                    'chunk_number': chunk_id,
                    'trace_range': (t_start, t_end),
                    'sample_range': (d_start, d_end),
                    'time_range_ms': (time_start, time_end),
                    'num_traces': t_end - t_start,
                    'num_samples': d_end - d_start,
                })
                chunk_id += 1
        
        return grid_chunks
    
    def extract_chunk(self, trace_range: Tuple[int, int], 
                     sample_range: Tuple[int, int]) -> np.ndarray:
        """
        특정 범위의 데이터 청크 추출
        
        Args:
            trace_range: (시작_트레이스, 종료_트레이스)
            sample_range: (시작_샘플, 종료_샘플)
            
        Returns:
            추출된 데이터 배열
        """
        t_start, t_end = trace_range
        s_start, s_end = sample_range
        
        num_traces = t_end - t_start
        num_samples = s_end - s_start
        
        data = np.zeros((num_traces, num_samples), dtype=np.float32)
        
        for i, trace_idx in enumerate(range(t_start, t_end)):
            trace_data = self.file.trace[trace_idx]
            data[i] = trace_data[s_start:s_end]
        
        return data
    
    def save_chunk_as_npy(self, data: np.ndarray, output_path: str, 
                         metadata: Optional[Dict] = None):
        """
        청크를 NumPy 파일로 저장
        
        Args:
            data: 저장할 데이터
            output_path: 출력 파일 경로 (.npy)
            metadata: 메타데이터 (별도의 .json 파일로 저장)
        """
        # 데이터 저장
        np.save(output_path, data)
        print(f"청크 저장: {output_path} (shape: {data.shape})")
        
        # 메타데이터 저장
        if metadata is not None:
            import json
            meta_path = output_path.replace('.npy', '_metadata.json')
            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            print(f"메타데이터 저장: {meta_path}")
    
    def save_all_chunks(self, chunks: List[Dict[str, Any]], output_dir: str, 
                       prefix: str = "chunk"):
        """
        모든 청크를 파일로 저장
        
        Args:
            chunks: 청크 정보 리스트 (divide_by_grid 결과)
            output_dir: 출력 디렉토리
            prefix: 파일명 접두사
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n총 {len(chunks)}개 청크를 '{output_dir}'에 저장합니다...\n")
        
        for chunk_info in chunks:
            chunk_num = chunk_info['chunk_number']
            trace_range = chunk_info['trace_range']
            sample_range = chunk_info['sample_range']
            
            # 데이터 추출
            data = self.extract_chunk(trace_range, sample_range)
            
            # 파일명 생성
            filename = f"{prefix}_{chunk_num:04d}.npy"
            output_path = os.path.join(output_dir, filename)
            
            # 메타데이터 준비
            metadata = {
                'chunk_id': chunk_info['chunk_id'],
                'chunk_number': chunk_num,
                'trace_range': trace_range,
                'sample_range': sample_range,
                'time_range_ms': chunk_info['time_range_ms'],
                'shape': data.shape,
                'source_file': self.filepath,
            }
            
            # 저장
            self.save_chunk_as_npy(data, output_path, metadata)
        
        print(f"\n모든 청크 저장 완료!")
    
    def print_division_info(self, chunks: List[Dict[str, Any]]):
        """분할 정보 출력"""
        print("=" * 80)
        print("DATA DIVISION INFORMATION")
        print("=" * 80)
        print(f"원본 파일: {self.filepath}")
        print(f"총 트레이스 수: {self.total_traces:,}")
        print(f"트레이스당 샘플 수: {self.samples_per_trace:,}")
        print(f"샘플 간격: {self.sample_interval:.3f} ms")
        print(f"\n총 청크 수: {len(chunks)}")
        print(f"\n첫 5개 청크 정보:")
        print("-" * 80)
        
        for chunk in chunks[:5]:
            t_start, t_end = chunk['trace_range']
            s_start, s_end = chunk['sample_range']
            time_start, time_end = chunk['time_range_ms']
            
            print(f"청크 #{chunk['chunk_number']:04d} | "
                  f"Traces: [{t_start:5d} - {t_end:5d}] ({chunk['num_traces']:4d} traces) | "
                  f"Samples: [{s_start:5d} - {s_end:5d}] ({chunk['num_samples']:4d} samples) | "
                  f"Time: [{time_start:7.2f} - {time_end:7.2f}] ms")
        
        if len(chunks) > 5:
            print(f"... (총 {len(chunks) - 5}개 청크 생략)")
        
        print("=" * 80)


def divide_segy_file(filepath: str, 
                     num_traces_per_chunk: int = 100,
                     depth_interval_ms: float = 500.0,
                     output_dir: Optional[str] = None,
                     save_chunks: bool = False) -> List[Dict[str, Any]]:
    """
    SEGY 파일을 간단하게 분할하는 함수
    
    Args:
        filepath: SEGY 파일 경로
        num_traces_per_chunk: 청크당 트레이스 수
        depth_interval_ms: 깊이/시간 분할 간격 (ms)
        output_dir: 출력 디렉토리 (None이면 저장 안 함)
        save_chunks: 청크를 파일로 저장할지 여부
        
    Returns:
        청크 정보 리스트
    """
    with SEGYDataDivider(filepath) as divider:
        # 그리드 분할
        chunks = divider.divide_by_grid(num_traces_per_chunk, depth_interval_ms)
        
        # 정보 출력
        divider.print_division_info(chunks)
        
        # 저장
        if save_chunks and output_dir is not None:
            divider.save_all_chunks(chunks, output_dir)
        
        return chunks


if __name__ == "__main__":
    # 사용 예제
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        num_traces = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        depth_interval = float(sys.argv[3]) if len(sys.argv) > 3 else 500.0
        
        print(f"SEGY 데이터 분할: {filepath}\n")
        print(f"청크당 트레이스 수: {num_traces}")
        print(f"깊이/시간 간격: {depth_interval} ms\n")
        
        # 분할 (저장하지 않음)
        chunks = divide_segy_file(filepath, num_traces, depth_interval)
        
        # 저장하려면
        # divide_segy_file(filepath, num_traces, depth_interval, 
        #                 output_dir="./output_chunks", save_chunks=True)
    else:
        print("사용법: python data_divide.py <segy_file_path> [num_traces_per_chunk] [depth_interval_ms]")
        print("예제: python data_divide.py data.segy 100 500")
