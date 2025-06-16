import os
import sys
import pyke.test


def run_all_tests():
    # 현재 디렉터리 또는 하위 디렉터리에서 .tst 파일들 찾기
    test_dirs = ['.']
    test_files = []
    for test_dir in test_dirs:
        for root, _, files in os.walk(test_dir):
            for file in files:
                if file.endswith('.tst'):
                    test_files.append(os.path.join(root, file))

    if not test_files:
        print("No .tst files found.")
        return

    # 테스트 실행
    print("Running tests...")
    errors = pyke.test.test_files(test_files, verbose=True)

    if errors:
        print(f"\n{len(errors)} error(s) found:")
        for error in errors:
            print(error)
        sys.exit(1)
    else:
        print("\nAll tests passed.")
        sys.exit(0)


if __name__ == "__main__":
    run_all_tests()
