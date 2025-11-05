"""
SEGY Header Loading Module
SEG-Y 파일의 헤더 정보를 로드하고 분석하는 모듈
"""

import segyio
import numpy as np
from typing import Dict, Any, Tuple
import struct


class SEGYHeaderLoader:
    """SEG-Y 헤더 정보를 로드하고 분석하는 클래스"""
    
    def __init__(self, filepath: str):
        """
        SEGYHeaderLoader 초기화
        
        Args:
            filepath: SEGY 파일 경로
        """
        self.filepath = filepath
        self.file = None
        self.header_info = {}
        
    def __enter__(self):
        """Context manager 진입"""
        self.file = segyio.open(self.filepath, ignore_geometry=True)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        if self.file:
            self.file.close()
    
    def load_textual_header(self) -> str:
        """
        Textual File Header 로드 (3200 bytes)
        
        Returns:
            텍스트 헤더 문자열
        """
        if not self.file:
            raise ValueError("파일이 열리지 않았습니다. with 문을 사용하세요.")
        
        text_header = self.file.text[0]
        return text_header
    
    def load_binary_header(self) -> Dict[str, Any]:
        """
        Binary File Header 로드 (400 bytes)
        
        Returns:
            바이너리 헤더 정보 딕셔너리
        """
        if not self.file:
            raise ValueError("파일이 열리지 않았습니다.")
        
        bin_header = self.file.bin
        
        header_dict = {
            'job_id': bin_header[segyio.BinField.JobID],
            'line_number': bin_header[segyio.BinField.LineNumber],
            'reel_number': bin_header[segyio.BinField.ReelNumber],
            'traces_per_ensemble': bin_header[segyio.BinField.Traces],
            'aux_traces_per_ensemble': bin_header[segyio.BinField.AuxTraces],
            'sample_interval': bin_header[segyio.BinField.Interval],  # 마이크로초 단위
            'samples_per_trace': bin_header[segyio.BinField.Samples],
            'data_sample_format': bin_header[segyio.BinField.Format],
            'ensemble_fold': bin_header[segyio.BinField.EnsembleFold],
            'sorting_code': bin_header[segyio.BinField.SortingCode],
            'measurement_system': bin_header[segyio.BinField.MeasurementSystem],
        }
        
        return header_dict
    
    def load_trace_header(self, trace_index: int = 0) -> Dict[str, Any]:
        """
        특정 Trace의 헤더 정보 로드 (240 bytes per trace)
        
        Args:
            trace_index: 트레이스 인덱스 (0부터 시작)
            
        Returns:
            트레이스 헤더 정보 딕셔너리
        """
        if not self.file:
            raise ValueError("파일이 열리지 않았습니다.")
        
        if trace_index >= len(self.file.trace):
            raise ValueError(f"트레이스 인덱스가 범위를 벗어났습니다. (최대: {len(self.file.trace) - 1})")
        
        trace_header = self.file.header[trace_index]
        
        header_dict = {
            'trace_sequence_line': trace_header[segyio.TraceField.TRACE_SEQUENCE_LINE],
            'trace_sequence_file': trace_header[segyio.TraceField.TRACE_SEQUENCE_FILE],
            'field_record': trace_header[segyio.TraceField.FieldRecord],
            'trace_number': trace_header[segyio.TraceField.TraceNumber],
            'ensemble_number': trace_header[segyio.TraceField.CDP],
            'inline_number': trace_header[segyio.TraceField.INLINE_3D],
            'crossline_number': trace_header[segyio.TraceField.CROSSLINE_3D],
            'x_coordinate': trace_header[segyio.TraceField.CDP_X],
            'y_coordinate': trace_header[segyio.TraceField.CDP_Y],
            'scalar_coordinate': trace_header[segyio.TraceField.SourceGroupScalar],
            'samples_in_trace': trace_header[segyio.TraceField.TRACE_SAMPLE_COUNT],
            'sample_interval': trace_header[segyio.TraceField.TRACE_SAMPLE_INTERVAL],
        }
        
        return header_dict
    
    def get_file_info(self) -> Dict[str, Any]:
        """
        전체 SEGY 파일의 기본 정보를 가져오기
        
        Returns:
            파일 정보 딕셔너리
        """
        if not self.file:
            raise ValueError("파일이 열리지 않았습니다.")
        
        bin_header = self.load_binary_header()
        
        # 샘플 간격을 초 단위로 변환
        sample_interval_us = bin_header['sample_interval']  # 마이크로초
        sample_interval_ms = sample_interval_us / 1000  # 밀리초
        
        # 총 트레이스 수
        total_traces = len(self.file.trace)
        
        # 트레이스당 샘플 수
        samples_per_trace = bin_header['samples_per_trace']
        
        # 데이터 포맷
        format_code = bin_header['data_sample_format']
        format_dict = {
            1: 'IBM floating point (4 bytes)',
            2: '4-byte integer',
            3: '2-byte integer',
            5: 'IEEE floating point (4 bytes)',
            8: '1-byte integer'
        }
        data_format = format_dict.get(format_code, f'Unknown ({format_code})')
        
        # 측정 시스템
        measurement_system = bin_header['measurement_system']
        measurement_dict = {
            1: 'Meters',
            2: 'Feet'
        }
        measurement = measurement_dict.get(measurement_system, 'Unknown')
        
        # 총 시간/깊이 범위
        total_time_depth = samples_per_trace * sample_interval_ms
        
        # 데이터 크기 계산 (MB)
        bytes_per_sample = {1: 4, 2: 4, 3: 2, 5: 4, 8: 1}.get(format_code, 4)
        total_data_size_mb = (total_traces * samples_per_trace * bytes_per_sample) / (1024 * 1024)
        
        info = {
            'filepath': self.filepath,
            'total_traces': total_traces,
            'samples_per_trace': samples_per_trace,
            'sample_interval_us': sample_interval_us,
            'sample_interval_ms': sample_interval_ms,
            'total_time_depth_ms': total_time_depth,
            'data_format': data_format,
            'format_code': format_code,
            'measurement_system': measurement,
            'total_data_size_mb': round(total_data_size_mb, 2),
            'binary_header': bin_header
        }
        
        self.header_info = info
        return info
    
    def print_header_summary(self):
        """헤더 정보 요약 출력"""
        info = self.get_file_info()
        
        print("=" * 60)
        print("SEGY FILE HEADER SUMMARY")
        print("=" * 60)
        print(f"파일 경로: {info['filepath']}")
        print(f"\n[데이터 크기]")
        print(f"  총 트레이스 수: {info['total_traces']:,}")
        print(f"  트레이스당 샘플 수: {info['samples_per_trace']:,}")
        print(f"  전체 데이터 크기: {info['total_data_size_mb']:,.2f} MB")
        print(f"\n[샘플링 정보]")
        print(f"  샘플 간격: {info['sample_interval_us']} μs ({info['sample_interval_ms']} ms)")
        print(f"  총 시간/깊이: {info['total_time_depth_ms']:.2f} ms")
        print(f"\n[데이터 포맷]")
        print(f"  포맷: {info['data_format']}")
        print(f"  측정 시스템: {info['measurement_system']}")
        print("=" * 60)
    
    def print_textual_header(self):
        """Textual Header 출력"""
        text = self.load_textual_header()
        print("\n" + "=" * 60)
        print("TEXTUAL FILE HEADER")
        print("=" * 60)
        print(text)
        print("=" * 60)
    
    def print_trace_header_sample(self, trace_index: int = 0):
        """특정 트레이스 헤더 샘플 출력"""
        trace_header = self.load_trace_header(trace_index)
        
        print(f"\n{'=' * 60}")
        print(f"TRACE HEADER SAMPLE (Trace #{trace_index})")
        print("=" * 60)
        for key, value in trace_header.items():
            print(f"  {key}: {value}")
        print("=" * 60)


def load_segy_header(filepath: str, verbose: bool = True) -> Dict[str, Any]:
    """
    SEGY 파일의 헤더 정보를 간단하게 로드하는 함수
    
    Args:
        filepath: SEGY 파일 경로
        verbose: 상세 정보 출력 여부
        
    Returns:
        파일 정보 딕셔너리
    """
    with SEGYHeaderLoader(filepath) as loader:
        info = loader.get_file_info()
        
        if verbose:
            loader.print_header_summary()
        
        return info


if __name__ == "__main__":
    # 사용 예제
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        print(f"SEGY 파일 분석: {filepath}\n")
        
        with SEGYHeaderLoader(filepath) as loader:
            # 헤더 정보 출력
            loader.print_header_summary()
            loader.print_textual_header()
            loader.print_trace_header_sample(0)
    else:
        print("사용법: python header_loading.py <segy_file_path>")
