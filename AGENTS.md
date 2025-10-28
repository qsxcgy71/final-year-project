# AGENTS — Project Contract

Single source of truth: PROJECT_ROADMAP.md + DECISIONS.md
Scope: X²-DFD → EFF++ (explainable, low‑cost fine‑tuning)

## Always read first
- PROJECT_ROADMAP.md
- DECISIONS.md
- progress.md
- CHECKPOINT.md

## Non-goals / Red lines
- 不修改未在“执行计划”中声明的文件
- 不凭空扩展数据来源；解释文本不得猜测身份/工具名
- 预算线：显存/时延超出则回退（见 PROJECT_ROADMAP.md）

## Default runbook
1) 读取上面四个文件并给出 目标/退出条件/回滚点  
2) 仅修改计划中的文件；产物落在既定路径  
3) 执行后更新 progress.md 与 DECISIONS.md（使用各自模板）

