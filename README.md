# hermes-webui-cn

> [English README →](./README.en.md)

[Hermes WebUI](https://github.com/nesquena/hermes-webui) 的中文本地化分支，默认中文界面，定期同步上游。

适合中国大陆用户：上游 zh 字典已较完整，本分支只在其上做"开箱即中文"的默认值调整与必要文档翻译，不做 UI 重写、不裁剪功能，便于跟随上游更新。

---

## 与上游的关系

- **上游**：[`nesquena/hermes-webui`](https://github.com/nesquena/hermes-webui)
- **当前基线**：`v0.51.30`
- **同步策略**：`scripts/sync-upstream.sh` 周期性 `git merge upstream/master`，本地化补丁以 `[CN-fork] P-XXX:` 前缀的提交叠加在 upstream 之上
- **本地化范围**：默认语言、登录页 locale 兜底、`<html lang>` 等"开箱即中文"相关的小改动；UI 字符串仍由上游 `static/i18n.js` 的 `zh` / `zh-Hant` 字典维护

完整本地化补丁列表见 [`MAINTAINING.md`](./MAINTAINING.md)。

## 快速开始

```bash
git clone https://github.com/Eynzof/hermes-webui-cn.git
cd hermes-webui-cn
python3 bootstrap.py
```

服务默认监听 `http://127.0.0.1:8787`，首次启动即为中文界面。

更详细的部署、配置环境变量、对接 hermes-agent 等内容，请参考 [上游英文 README](./README.en.md)——本分支不修改部署逻辑，所有运行手册仍以上游为准。

## 检查更新走哪？

WebUI 内置的"检查更新"功能（`/api/updates/check`、`/api/updates/apply`、`/api/updates/force`）完全基于本地 `git remote origin` 工作，没有任何硬编码的远端地址：

- 从 cnb.cool 克隆 → `origin` = cnb → 检查 / 拉取 / 强制更新都自动走 cnb，无需配置
- 从 GitHub 克隆 → `origin` = GitHub → 想改走 cnb 一条命令即可：

```bash
git remote set-url origin https://cnb.cool/hermesagent-cn/hermes-webui-cn-mirror.git
```

切换后 `git fetch origin` 与 WebUI 设置面板里的"检查更新"按钮都会改走 cnb 镜像。cnb 镜像每 6 小时从 GitHub 自动同步一次，落后窗口最多 6h。

### ⚠️ 一次性升级提醒（2026-05-12 之前 clone 的老用户）

2026-05-12 对 `main` 历史做过一次 rebase 整理（P-001 ~ P-011 重新 base 到新上游基线），并 force-push 到 `origin/main`。结果是：老用户本地 HEAD 已不在远端历史里，**普通的"立即更新"无法 fast-forward**。

- **症状**：WebUI 设置 → 检查更新 → 点"立即更新"，提示 `not possible to fast-forward` / `diverged`
- **解决**：失败提示下方会出现 **"Force update"** 按钮，点一次即可（内部执行 `git reset --hard origin/main`）
- **注意**：`reset --hard` 会丢弃未提交的本地改动，如有自定义请先备份
- 之后所有更新会恢复正常的 fast-forward，无需再次强制

## 反馈

- 上游 bug / 通用功能问题 → 直接给 [`nesquena/hermes-webui`](https://github.com/nesquena/hermes-webui/issues) 提
- 仅本地化层 / 中文相关问题 → 给本仓库提 issue
