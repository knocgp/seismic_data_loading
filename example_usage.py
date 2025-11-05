#!/usr/bin/env python3
"""
SEGY Processing Example Usage
SEGY 파일 처리 예제 스크립트
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# 모듈 import
from header_loading import SEGYHeaderLoader, load_segy_header
from data_loading import SEGYDataLoader, load_segy_data
from data_divide import SEGYDataDivider, divide_segy_file


def example_1_basic_header_analysis(segy_file: str):
    """
    예제 1: 기본 헤더 분석
    """
    print("\n" + "="*70)
    print("예제 1: 기본 헤더 분석")
    print("="*70)
    
    # 간단한 방법
    info = load_segy_header(segy_file, verbose=True)
    
    # 또는 클래스 사용
    with SEGYHeaderLoader(segy_file) as loader:
        loader.print_textual_header()
        loader.print_trace_header_sample(0)
    
    return info


def example_2_data_loading(segy_file: str):
    """
    예제 2: 데이터 로드 및 시각화
    """
    print("\n" + "="*70)
    print("예제 2: 데이터 로드 및 시각화")
    print("="*70)
    
    with SEGYDataLoader(segy_file) as loader:
        # 데이터 정보 출력
        loader.print_data_info(include_stats=True)
        
        # 처음 100개 트레이스 로드
        num_traces = min(100, loader.total_traces)
        data = loader.load_traces(0, num_traces)
        time_axis = loader.get_time_axis()
        
        print(f"\n로드된 데이터 형태: {data.shape}")
        
        # 시각화
        plt.figure(figsize=(12, 6))
        plt.imshow(data.T, aspect='auto', cmap='seismic',
                   extent=[0, num_traces, time_axis[-1], time_axis[0]],
                   vmin=-np.percentile(np.abs(data), 95),
                   vmax=np.percentile(np.abs(data), 95))
        plt.colorbar(label='Amplitude')
        plt.xlabel('Trace Number')
        plt.ylabel('Time/Depth (ms)')
        plt.title(f'SEGY Data (First {num_traces} Traces)')
        plt.tight_layout()
        
        # 저장
        output_file = 'example_seismic_section.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"\n시각화 이미지 저장: {output_file}")
        plt.close()
    
    return data


def example_3_data_division(segy_file: str):
    """
    예제 3: 데이터 분할
    """
    print("\n" + "="*70)
    print("예제 3: 데이터 분할")
    print("="*70)
    
    # 분할 파라미터
    traces_per_chunk = 100
    depth_interval_ms = 500.0
    
    with SEGYDataDivider(segy_file) as divider:
        # 분할
        chunks = divider.divide_by_grid(traces_per_chunk, depth_interval_ms)
        
        # 정보 출력
        divider.print_division_info(chunks)
        
        # 첫 번째 청크 추출 및 시각화
        if len(chunks) > 0:
            chunk = chunks[0]
            chunk_data = divider.extract_chunk(
                chunk['trace_range'],
                chunk['sample_range']
            )
            
            print(f"\n첫 번째 청크 데이터 형태: {chunk_data.shape}")
            
            # 청크 시각화
            t_start, t_end = chunk['trace_range']
            time_start, time_end = chunk['time_range_ms']
            
            plt.figure(figsize=(10, 6))
            plt.imshow(chunk_data.T, aspect='auto', cmap='seismic',
                       extent=[t_start, t_end, time_end, time_start],
                       vmin=-np.percentile(np.abs(chunk_data), 95),
                       vmax=np.percentile(np.abs(chunk_data), 95))
            plt.colorbar(label='Amplitude')
            plt.xlabel('Trace Number')
            plt.ylabel('Time/Depth (ms)')
            plt.title(f'Chunk #0 Visualization')
            plt.tight_layout()
            
            output_file = 'example_chunk_0.png'
            plt.savefig(output_file, dpi=150, bbox_inches='tight')
            print(f"청크 시각화 이미지 저장: {output_file}")
            plt.close()
    
    return chunks


def example_4_save_chunks(segy_file: str, output_dir: str = './output_chunks'):
    """
    예제 4: 청크 저장
    """
    print("\n" + "="*70)
    print("예제 4: 청크 저장")
    print("="*70)
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 분할 및 저장
    chunks = divide_segy_file(
        segy_file,
        num_traces_per_chunk=100,
        depth_interval_ms=500.0,
        output_dir=output_dir,
        save_chunks=True
    )
    
    print(f"\n총 {len(chunks)}개 청크가 '{output_dir}'에 저장되었습니다.")
    
    # 저장된 파일 확인
    saved_files = list(Path(output_dir).glob('*.npy'))
    print(f"저장된 파일 개수: {len(saved_files)}")
    
    if saved_files:
        print(f"\n예시 파일:")
        for f in saved_files[:3]:
            file_size_mb = f.stat().st_size / (1024 * 1024)
            print(f"  - {f.name} ({file_size_mb:.2f} MB)")
    
    return chunks


def example_5_trace_visualization(segy_file: str):
    """
    예제 5: 개별 트레이스 시각화
    """
    print("\n" + "="*70)
    print("예제 5: 개별 트레이스 시각화")
    print("="*70)
    
    with SEGYDataLoader(segy_file) as loader:
        # 여러 위치의 트레이스 선택
        total_traces = loader.total_traces
        trace_indices = [
            0,
            total_traces // 4,
            total_traces // 2,
            total_traces * 3 // 4
        ]
        trace_indices = [t for t in trace_indices if t < total_traces]
        
        time_axis = loader.get_time_axis()
        
        # 플롯
        fig, axes = plt.subplots(1, len(trace_indices), 
                                figsize=(16, 6), sharey=True)
        
        if len(trace_indices) == 1:
            axes = [axes]
        
        for i, trace_idx in enumerate(trace_indices):
            trace_data = loader.load_trace(trace_idx)
            
            axes[i].plot(trace_data, time_axis, 'b-', linewidth=0.5)
            axes[i].fill_betweenx(time_axis, 0, trace_data, 
                                 where=(trace_data > 0),
                                 color='red', alpha=0.5)
            axes[i].fill_betweenx(time_axis, 0, trace_data, 
                                 where=(trace_data < 0),
                                 color='blue', alpha=0.5)
            axes[i].set_xlabel('Amplitude')
            axes[i].set_title(f'Trace #{trace_idx}')
            axes[i].grid(True, alpha=0.3)
            axes[i].invert_yaxis()
        
        axes[0].set_ylabel('Time/Depth (ms)')
        plt.tight_layout()
        
        output_file = 'example_traces.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"트레이스 시각화 이미지 저장: {output_file}")
        plt.close()


def example_6_amplitude_analysis(segy_file: str):
    """
    예제 6: 진폭 분석
    """
    print("\n" + "="*70)
    print("예제 6: 진폭 분석")
    print("="*70)
    
    with SEGYDataLoader(segy_file) as loader:
        # 샘플링하여 로드
        sample_traces = min(1000, loader.total_traces)
        data = loader.load_traces(0, sample_traces)
        
        # 통계 계산
        stats = loader.get_data_statistics(data)
        
        print("\n진폭 통계:")
        for key, value in stats.items():
            if key in ['shape', 'dtype']:
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value:.6e}")
        
        # 히스토그램
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # 히스토그램
        axes[0].hist(data.flatten(), bins=100, edgecolor='black', alpha=0.7)
        axes[0].set_xlabel('Amplitude')
        axes[0].set_ylabel('Frequency')
        axes[0].set_title('Amplitude Distribution')
        axes[0].grid(True, alpha=0.3)
        
        # 박스 플롯
        axes[1].boxplot([data.flatten()], vert=True)
        axes[1].set_ylabel('Amplitude')
        axes[1].set_title('Amplitude Box Plot')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        output_file = 'example_amplitude_analysis.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"\n진폭 분석 이미지 저장: {output_file}")
        plt.close()


def main():
    """메인 함수"""
    print("\n" + "="*70)
    print("SEGY Processing Examples")
    print("="*70)
    
    # SEGY 파일 경로 확인
    if len(sys.argv) < 2:
        print("\n사용법: python example_usage.py <segy_file_path>")
        print("예제: python example_usage.py data.segy")
        return
    
    segy_file = sys.argv[1]
    
    # 파일 존재 확인
    if not os.path.exists(segy_file):
        print(f"\n오류: 파일을 찾을 수 없습니다: {segy_file}")
        return
    
    print(f"\nSEGY 파일: {segy_file}")
    
    try:
        # 예제 실행
        print("\n모든 예제를 실행합니다...")
        
        # 예제 1: 헤더 분석
        info = example_1_basic_header_analysis(segy_file)
        
        # 예제 2: 데이터 로드 및 시각화
        data = example_2_data_loading(segy_file)
        
        # 예제 3: 데이터 분할
        chunks = example_3_data_division(segy_file)
        
        # 예제 4: 청크 저장 (사용자 선택)
        save_chunks = input("\n청크를 파일로 저장하시겠습니까? (y/n): ").lower() == 'y'
        if save_chunks:
            example_4_save_chunks(segy_file)
        
        # 예제 5: 트레이스 시각화
        example_5_trace_visualization(segy_file)
        
        # 예제 6: 진폭 분석
        example_6_amplitude_analysis(segy_file)
        
        print("\n" + "="*70)
        print("모든 예제 완료!")
        print("="*70)
        print("\n생성된 파일:")
        output_files = [
            'example_seismic_section.png',
            'example_chunk_0.png',
            'example_traces.png',
            'example_amplitude_analysis.png'
        ]
        for f in output_files:
            if os.path.exists(f):
                print(f"  ✓ {f}")
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
