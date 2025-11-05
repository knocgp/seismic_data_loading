#!/usr/bin/env python3
"""
Create Mini SEGY Sample File
테스트용 작은 SEGY 파일을 생성하는 스크립트
"""

import segyio
import numpy as np
import os
import sys


def create_mini_segy(output_file='mini_sample.segy', 
                     n_traces=50, 
                     n_samples=250,
                     sample_interval_us=2000):
    """
    테스트용 미니 SEGY 파일 생성
    
    Args:
        output_file: 출력 파일명
        n_traces: 트레이스 수 (기본 50)
        n_samples: 샘플 수 (기본 250)
        sample_interval_us: 샘플 간격 (마이크로초, 기본 2000 = 2ms)
    """
    print(f"미니 SEGY 샘플 파일 생성 중...")
    print(f"  출력 파일: {output_file}")
    print(f"  트레이스 수: {n_traces}")
    print(f"  샘플 수: {n_samples}")
    print(f"  샘플 간격: {sample_interval_us} μs ({sample_interval_us/1000} ms)")
    
    # Spec 생성
    spec = segyio.spec()
    spec.format = 5  # IEEE float
    spec.sorting = 2  # CDP sorted
    spec.samples = range(n_samples)
    spec.ilines = range(n_traces)
    spec.xlines = range(1)
    
    with segyio.create(output_file, spec) as f:
        # 텍스트 헤더 생성 (3200 bytes)
        lines = [
            "C01 MINI SEGY SAMPLE FILE FOR TESTING                                   ",
            "C02 Created with Python segyio library                                  ",
            "C03 GitHub: knocgp/seismic_data_loading                                 ",
            "C04                                                                      ",
            "C05 FILE INFORMATION:                                                    ",
            f"C06 Number of traces: {n_traces:<55}",
            f"C07 Samples per trace: {n_samples:<52}",
            f"C08 Sample interval: {sample_interval_us} microseconds ({sample_interval_us/1000} ms)            ",
            "C09                                                                      ",
            "C10 DATA CONTENT:                                                        ",
            "C11 Synthetic seismic data with sine waves and random noise             ",
            "C12 For testing and demonstration purposes only                         ",
            "C13                                                                      ",
            "C14 LICENSE: MIT                                                         ",
            "C15                                                                      ",
        ]
        
        # 나머지 줄을 공백으로 채움 (C16 ~ C40)
        for i in range(len(lines), 40):
            lines.append(f"C{i+1:02d} " + " " * 77)
        
        text_header = "".join(lines)
        text_header = text_header[:3200].ljust(3200)  # 정확히 3200 바이트
        f.text[0] = text_header
        
        # 바이너리 헤더
        f.bin = {
            segyio.BinField.JobID: 1,
            segyio.BinField.LineNumber: 1,
            segyio.BinField.ReelNumber: 1,
            segyio.BinField.Traces: n_traces,
            segyio.BinField.AuxTraces: 0,
            segyio.BinField.Interval: sample_interval_us,
            segyio.BinField.Samples: n_samples,
            segyio.BinField.Format: 5,  # IEEE floating point
            segyio.BinField.EnsembleFold: 1,
            segyio.BinField.SortingCode: 2,  # CDP sorted
            segyio.BinField.MeasurementSystem: 1,  # Meters
        }
        
        # 트레이스 데이터 생성
        print("\n트레이스 데이터 생성 중...")
        for i in range(n_traces):
            # 복합 신호 생성
            t = np.linspace(0, n_samples * sample_interval_us / 1000000, n_samples)
            
            # 다양한 주파수의 사인파 조합
            freq1 = 20 + (i % 10) * 5  # 20-65 Hz
            freq2 = 10 + (i % 5) * 3   # 10-22 Hz
            
            signal1 = np.sin(2 * np.pi * freq1 * t)
            signal2 = 0.5 * np.sin(2 * np.pi * freq2 * t)
            noise = np.random.normal(0, 0.1, n_samples)
            
            # 시간에 따른 감쇠 추가 (실제 지진파 특성)
            decay = np.exp(-t * 2)
            
            # 최종 트레이스 데이터
            trace_data = (signal1 + signal2) * decay + noise
            
            # 정규화
            if np.max(np.abs(trace_data)) > 0:
                trace_data = trace_data / np.max(np.abs(trace_data))
            
            f.trace[i] = trace_data.astype(np.float32)
            
            # 트레이스 헤더
            f.header[i] = {
                segyio.TraceField.TRACE_SEQUENCE_LINE: i + 1,
                segyio.TraceField.TRACE_SEQUENCE_FILE: i + 1,
                segyio.TraceField.FieldRecord: 1,
                segyio.TraceField.TraceNumber: i + 1,
                segyio.TraceField.CDP: i + 1,
                segyio.TraceField.INLINE_3D: i + 1,
                segyio.TraceField.CROSSLINE_3D: 1,
                segyio.TraceField.CDP_X: i * 25,  # 25m 간격
                segyio.TraceField.CDP_Y: 0,
                segyio.TraceField.SourceGroupScalar: -100,  # 1/100 스케일
                segyio.TraceField.TRACE_SAMPLE_COUNT: n_samples,
                segyio.TraceField.TRACE_SAMPLE_INTERVAL: sample_interval_us,
            }
            
            # 진행상황 표시
            if (i + 1) % 10 == 0 or i == n_traces - 1:
                print(f"  진행: {i+1}/{n_traces} 트레이스 완료")
    
    # 파일 크기 확인
    file_size = os.path.getsize(output_file)
    file_size_kb = file_size / 1024
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"\n✅ 미니 SEGY 파일 생성 완료!")
    print(f"   파일: {output_file}")
    if file_size_mb >= 1:
        print(f"   크기: {file_size_mb:.2f} MB")
    else:
        print(f"   크기: {file_size_kb:.2f} KB")
    print(f"   트레이스: {n_traces}")
    print(f"   샘플/트레이스: {n_samples}")
    print(f"   전체 데이터 포인트: {n_traces * n_samples:,}")


def create_multiple_samples():
    """여러 크기의 샘플 파일 생성"""
    samples = [
        ("mini_sample_tiny.segy", 20, 100),      # ~8 KB
        ("mini_sample_small.segy", 50, 250),     # ~50 KB
        ("mini_sample_medium.segy", 100, 500),   # ~200 KB
        ("mini_sample_large.segy", 200, 1000),   # ~800 KB
    ]
    
    print("=" * 70)
    print("여러 크기의 샘플 파일 생성")
    print("=" * 70)
    
    for filename, n_traces, n_samples in samples:
        print()
        create_mini_segy(filename, n_traces, n_samples)
        print()
    
    print("=" * 70)
    print("모든 샘플 파일 생성 완료!")
    print("=" * 70)
    
    # 파일 목록 출력
    print("\n생성된 파일:")
    for filename, _, _ in samples:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            if size >= 1024 * 1024:
                size_str = f"{size / (1024 * 1024):.2f} MB"
            else:
                size_str = f"{size / 1024:.2f} KB"
            print(f"  ✓ {filename:<30} ({size_str})")


def main():
    """메인 함수"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--multiple":
            # 여러 샘플 생성
            create_multiple_samples()
        elif sys.argv[1] == "--help":
            print("사용법:")
            print("  python create_sample_segy.py                          # 기본 샘플 생성")
            print("  python create_sample_segy.py --multiple               # 여러 크기 샘플 생성")
            print("  python create_sample_segy.py <file> <traces> <samples> # 커스텀 샘플")
            print("\n예제:")
            print("  python create_sample_segy.py mini.segy 100 500")
        else:
            # 커스텀 파라미터
            output_file = sys.argv[1] if len(sys.argv) > 1 else "mini_sample.segy"
            n_traces = int(sys.argv[2]) if len(sys.argv) > 2 else 50
            n_samples = int(sys.argv[3]) if len(sys.argv) > 3 else 250
            
            create_mini_segy(output_file, n_traces, n_samples)
    else:
        # 기본 샘플 생성
        create_mini_segy()
        
        print("\n💡 다른 크기의 샘플을 생성하려면:")
        print("   python create_sample_segy.py --multiple")


if __name__ == "__main__":
    main()
