# 自动化测试说明

本目录包含用于自动化测试 `FishROS Install` 项目的脚本和配置文件。

## 文件说明

- `test_runner.py`: 主测试运行器，负责执行所有测试用例并生成报告。
- `fish_install_test.yaml`: 测试配置文件，定义了不同系统版本下的测试用例。
- `generate_report.py`: 用于生成 HTML 格式的测试报告。
- `test_report.json`: 测试运行后生成的 JSON 格式报告。
- `test_report.html`: 测试运行后生成的 HTML 格式报告。

## 运行测试

在项目根目录下执行以下命令来运行测试：

```bash
cd tests
python3 test_runner.py
```

### 指定目标系统版本

可以通过 `--target-os-version` 参数指定要测试的 Ubuntu 版本代号：

```bash
python3 test_runner.py --target-os-version focal
```

## 测试配置文件

`fish_install_test.yaml` 文件定义了测试用例。每个测试用例包含以下信息：

- `name`: 测试用例名称。
- `target_os_version`: 目标系统版本代号 (可选，如果不指定则适用于所有系统)。
- `chooses`: 一个列表，包含在安装过程中需要自动选择的选项。

### 配置文件易错点提醒

1. `chooses` 列表中的 `choose` 值必须与 `install.py` 中 `tools` 字典的键值对应。
2. `target_os_version` 必须是有效的 Ubuntu 版本代号（如 `bionic`, `focal`, `jammy` 等），目前仅支持ubuntu系列。
3. `desc` 字段虽然不是必须的，但建议填写以方便理解。
4. 在添加新的测试用例时，确保 `chooses` 中的选项序列能够完整地执行一个安装流程，避免因选项不当导致测试中断。

## 自动化测试与用户实际安装的区别

自动化测试与用户实际安装在以下方面有所不同：

1. **配置文件**: 自动化测试使用 `FISH_INSTALL_CONFIG` 环境变量指定的配置文件，而用户实际安装时会交互式地选择选项并生成配置文件。
2. **环境变量**: 自动化测试会设置特定的环境变量（如 `FISH_INSTALL_CONFIG`），而用户实际安装时不会。
3. **跳过某些步骤**: 在自动化测试环境中，会跳过一些需要用户交互的步骤，例如生成配置文件的确认提示。
4. **GitHub Actions**: 在 GitHub Actions 中运行时，会进一步跳过一些步骤以适应 CI/CD 环境。

## 工作原理

1. `test_runner.py` 会读取 `fish_install_test.yaml` 文件，加载所有适用于当前系统版本的测试用例。
2. 对于每个测试用例，`test_runner.py` 会创建一个临时的 `fish_install.yaml` 配置文件，其中包含该测试用例的 `chooses` 信息。
3. 然后，`test_runner.py` 会运行 `../install.py` 脚本，并通过环境变量 `FISH_INSTALL_CONFIG` 指定使用临时配置文件。
4. `install.py` 会根据配置文件中的选项自动执行安装过程，无需人工干预。
5. 测试运行结束后，`test_runner.py` 会生成 JSON 和 HTML 格式的测试报告。

## GitHub Actions 集成

本测试套件已集成到 GitHub Actions 中，每次推送代码时都会自动运行。工作流文件位于 `.github/workflows/test-install.yml`。