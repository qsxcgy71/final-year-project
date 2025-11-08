# DECISIONS 路 Project Logbook

浣跨敤璇存槑锛氭瘡褰撳舰鎴愨€滃彲浼犳挱鐨勫喅瀹氣€濓紝鎸変笅杩版ā鏉胯拷鍔犱竴鏉★紱闈炲喅瀹氭€х鐗囪鍐欏叆 progress.md銆? 
鏉＄洰妯℃澘瑙佹湰鏂囦欢姝ｆ枃锛涚儹鍚姩璇诲簭瑙?AGENTS.md 涓?codex.md銆? 
鏈€杩戞洿鏂帮細2025-11-08

## Index
- [2025-11-08] Stage 1 Gemini 批次 065-084 覆盖
- [2025-10-30] Stage 1 QA 与解释通路确认
- [2025-10-28] Stage 1 鏁版嵁娴佹按绾匡細EFF++ dataloader 涓庢枃鏈寚鏍囪剼鏈?- [2025-10-28] Stage 1 鍩虹鍚堝苟锛氭暣鍚?roadmap.md 鈫?PROJECT_ROADMAP.md
- [2025-10-28] 鍒濆鍖栵細閲囩敤 PROJECT_ROADMAP.md 浣滀负鍞竴鏉冨▉璺嚎鍥?
---

## [2025-10-28] Stage 1 鏁版嵁娴佹按绾匡細EFF++ dataloader 涓庢枃鏈寚鏍囪剼鏈?**鑳屾櫙**锛歋tage 1 鍓╀綑宸ヤ綔闇€瑕佽璇勬祴鑴氭湰璇诲彇鍥惧儚-鏂囨湰瀵癸紝骞跺娉ㄩ噴璐ㄩ噺鍋氳嚜鍔ㄥ寲浣撴銆? 
**鍐崇瓥**锛氭柊澧?`code/effpp_dataset.py`锛堝抚绾?Dataset + CLI锛変笌 `code/eval_effpp_annotations.py`锛圷es/No銆佽瘝鏁般€佹爣绛惧悎娉曟€х粺璁★紝杈撳嚭 `reports/effpp_annotation_metrics.{json,md}`锛夈€? 
**褰卞搷**锛歞ataloader 瀛愪换鍔″畬鎴愶紝璇勪及鑴氭湰鍙洿鎺ュ鐢紱QA 闈㈡澘浠嶉渶浜哄伐鎶芥煡涓庤瑙夌‘璁ゃ€? 
**鍥炴粴鏉′欢**锛氳嫢鍚庣画鏀圭敤鍦ㄧ嚎瑁佸壀鑰屼笉澶嶇敤缂撳瓨锛岄渶瑕佸悓姝ヨ皟鏁?dataset 瀹炵幇锛屽彲鍒囨崲鑷?`code/effpp_crop.py` 閲嶆瀯浜х墿銆?
---

## [2025-10-28] Stage 1 鍩虹鍚堝苟锛氭暣鍚?roadmap.md 鈫?PROJECT_ROADMAP.md
**鑳屾櫙**锛歋tage 1 宸插畬鎴愬抚瀵归綈涓庢敞閲婂師鍨嬶紝浣嗘棫鐗?`roadmap.md` 浠嶄繚鐣欑嫭绔嬩换鍔℃竻鍗曪紝鐘舵€佸垎鏁ｃ€? 
**鍐崇瓥**锛氬皢鏃?roadmap 浠诲姟骞跺叆 `PROJECT_ROADMAP.md`锛堣ˉ鍏?dataloader 妫€鏌ャ€佹枃鏈瘎浠烽挬瀛愮瓑鏉＄洰锛夛紝鍘嗗彶鍐呭褰掓。鍒?`docs/archive/ROADMAP_FFPP_LEGACY.md`锛屾牴鐩綍 `roadmap.md` 鏀逛负鎸囧悜璇存槑銆? 
**褰卞搷**锛氳矾绾垮浘涓庡閫夋闆嗕腑鍒板崟涓€鏂囦欢锛汼tage 1 鍓╀綑寰呭姙鑱氱劍 QA 闈㈡澘 / dataloader 鏀寔 / 鏂囨湰鎸囨爣鎺ュ叆锛涘悗缁彧闇€缁存姢 `PROJECT_ROADMAP.md` 涓庢湰鏃ュ織銆? 
**鍥炴粴鏉′欢**锛氳嫢鍥㈤槦浠嶉渶骞惰缁存姢 FF++ 涓撶敤璺嚎锛屽彲浠庡綊妗ｆ仮澶嶆棫鏂囦欢骞跺湪鐙珛鍒嗘敮缁存姢锛屼絾闇€閬垮厤鍙屽ご绠＄悊銆?
---

## [2025-10-28] 鍒濆鍖栵細閲囩敤 PROJECT_ROADMAP.md 浣滀负鍞竴鏉冨▉璺嚎鍥?**鑳屾櫙**锛氭棫鐗?`roadmap.md` 浠呰鐩?FF++锛屾柊鐗堟湰寮曞叆 EFF++ 涓庡洓闃舵鏂规銆? 
**鍐崇瓥**锛氭柊寤?`PROJECT_ROADMAP.md` 骞惰涓哄敮涓€鏉冨▉锛涙棫鏂囧綊妗ｄ负 `docs/archive/ROADMAP_FFPP_LEGACY.md`銆? 
**褰卞搷**锛氬悗缁换鍔′互鏂拌矾绾垮浘涓哄噯锛汼tage 0 浠嶄繚鐣?FF++ 浣滀负鍥炲綊鍩虹嚎銆? 
**鍥炴粴鏉′欢**锛氳嫢涓€鍛ㄥ唴鏃犳硶璺戦€?EFF++ 璇勬祴鑴氭湰锛屽彲鏆傛椂鍥為€€鍒?FF++ 娴佹按绾跨户缁敹灏俱€?
---

## [yyyy-mm-dd] 闃舵/涓婚锛堜緥濡傦細Stage 1 QA 闈㈡澘閫氳繃锛?**鍋囪/鐩爣**锛氣€? 
**鎿嶄綔**锛氣€︼紙鑴氭湰銆佸弬鏁般€佹牱鏈噺锛? 
**瑙傚療鍒扮殑缁撴灉**锛氣€︼紙BA / AUC / AP / r_pb / 瑙ｉ噴瀵归綈鎸囨爣锛? 
**缁撹锛堟槸鍚﹁揪鎴愰€€鍑烘潯浠讹級**锛氣€? 
**褰卞搷闈?*锛氣€︼紙鍙楀奖鍝嶇殑妯″潡/鏁版嵁/鏂囨。锛? 
**鍥炴粴鏉′欢**锛氣€︼紙瑙﹀彂鍥炴粴鐨勫満鏅級
## [2025-10-30] Stage 1 QA 与解释通路确认
**背景**：GPU 版 RetinaFace 重裁剪与 Schema 校验完成，需要确认 Stage 1 退出条件并决定解释生成策略。
**决策**：接受当前 placeholder 文本作为 Stage 1 基线，立即记录指标/QA 结果并进入 Stage 2 准备；同时指定 Gemini 2.5 Flash（`gemini-2.5-flash`）为正式解释模型，运行脚本时使用 `mode=chatgpt` 并从 `.env` 加载 `GEMINI_API_KEY` / `LLM_API_BASE`，待授权可用后替换 placeholder。
**观察**：复核 `reports/effpp_alignment_report.md` 与 `data/effpp_ann/train/Face2Face/910/frame_0000.ann.json` 等样本时，回答仍为 “Yes, explanation pending”，未包含部位+伪迹细节；`reports/effpp_annotation_metrics_{train,val,test}.json` 指标保持 100%，GPU 裁剪日志 `logs/effpp_prepare_faces_20251030_165218.log` 结束时间 17:36:38。
**影响面**：Stage 1 Must/指标项已勾选，后续 Stage 2 以此基线对比；解释文本需在 Gemini 或 LLaVA 跑通后整体刷新，刷新后需重跑评估脚本。
**后续**：修复 LLaVA 7B 4bit 推理报错（tokenizer 解析失败）并优先在小样本上验证 `code/effpp_explain.py --mode llava`，若仍失败则回退到 Gemini API 路径。
**回滚条件**：若在 Stage 2/3 前仍无法产出真实解释文本，则回退到 placeholder 基线并重新评估 API 或模型镜像状态。
## [2025-10-30] Stage 2 Prompt Injection 计划草案
**背景**：Stage 1 数据/解释基线已固定，需提前列出 PEFT 实验格点与评估通路。
**计划**：
- 学习率 × 提示长度网格：lr ∈ {5e-4, 1e-3, 2e-3}；prompt_len ∈ {16, 32, 48}，固定 seed 42。
- 入口脚本：`code/run_peft_prompt.py`（待编写），输出落在 `experiments/effpp_peft/<config>/`，并调用 `code/eval_effpp_annotations.py`、`eval/effpp_peft/metrics.json` 汇总分类+解释指标。
- 验证流程：每个配置在 val split 上评估 BA/AUC/解释一致性；训练日志写入 `<config>/train.log`，评估结果追加到 `reports/effpp_peft_grid.md`。
**后续**：完成脚本骨架后在 DECISIONS.md 更新执行记录，与 Stage 1 基线对比。必要时引入 Gemini 2.5 Flash 生成解释用于一体化评估。
**回滚条件**：若 GPU 显存或时间预算超标，优先保留 prompt_len=32，lr={5e-4,1e-3} 的子网格，并记录未跑项。

## [2025-11-03] LLaVA tokenizer fallback 与烟雾测试
**背景**：运行 code/effpp_explain.py --mode llava 时，	okenizer.json 在 tokenizers 0.19.1 上解析失败，阻塞模型加载；同时 4bit 量化依赖 bitsandbytes 与 Torch 2.4.0 组合报 is_power_of_2 缺失。
**决策**：在 code/llava_quant.py 中强制 AutoTokenizer(use_fast=False) + CLIPImageProcessor 组装处理器；临时采用 --quant none 路径跑小样本，并记录 4bit 报错供后续升级 bitsandbytes 或改用 AWQ/GPTQ。
**观察**：python code/effpp_explain.py --mode llava --identities 910 --max-frames 1 --quant none 成功生成输出（目录 data/effpp_ann_llava_test/...），文本含伪迹细节但存在重复句；FP16 加载约 48s 且显存压力较大。
**影响面**：LLaVA 通路可用于 placeholder 替换验证；量化未解前需分段跑或转向 Gemini 2.5 Flash 以满足预算。llava_quant.py 改动要求 slow tokenizer 依赖，可复用。
**回滚条件**：若无法在预算内跑完 FP16 且无可用量化方案，则暂回 placeholder 基线并优先推进 Gemini 2.5 Flash API。
## [2025-11-03] Gemini 2.5 Flash API 联通确认
**背景**：Stage 1 需要真实解释文本；官方 Gemini 2.5 Flash API 是预定替换方案，需先验证密钥与端点可用性并完成小批量写入测试。
**决策**：直接调用 `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`，使用 `.env` 中的 `GEMINI_API_KEY` 发起最小请求；若失败再回退到 `LLM_API_BASE` 代理。实际测试首选端点即返回 200，因此暂不启用备选路径。
**观察**：命令行 Python requests 返回文本 “Hello there!”（HTTP 200），随后以 `python code/effpp_explain.py --mode chatgpt --chatgpt-provider gemini --chatgpt-model gemini-2.5-flash --identities 910 --max-frames 1` 生成样例注释，文件落在 `data/effpp_ann_gemini_test/...`，run_meta 记录 `llm_provider=gemini`、`llm_base_url=https://generativelanguage.googleapis.com/...`。
**影响面**：可以将 Gemini 2.5 Flash 作为 `code/effpp_explain.py --mode chatgpt` 的后端，实现 placeholder → 真实解释的替换；run_meta 需写入 model_id=`gemini-2.5-flash` 与 base URL，source 字段标记 `api`。
**回滚条件**：若后续触发配额或速率限制，可切换到 #other APIs 中的代理地址或回退至 LLaVA FP16 分段执行。

## [2025-11-03] Gemini 多密钥节流策略
**背景**：批量生成时频繁触发 429/503（RPM/Daily），需在保持文本质量的同时减少限流错误，并利用新增的 `GEMINI_API_KEY_2~4`。
**决策**：`code/effpp_explain.py` 新增节流与重试：默认 request_interval=6.5s、指数退避；遇到 429/503 时自动切换到下一枚 GEMINI key（从 `_2` 开始轮询），run_meta 记录 `llm_active_key_index` 与 key 池大小。
**观察**：手动测试 key2~key4 均返回 200；批次运行 identity 020–029 时大多数请求成功（13 个身份完成），但在 key 轮换后仍触发项目级 `RESOURCE_EXHAUSTED`——说明 Free Tier 250/day 限制为项目共享，额外 key 只能在接力层面提供容错，无法突破日额度。
**影响面**：节流与轮换逻辑将持续生效，无需改动调用脚本；当额度恢复或配额提升时即可继续批量生成，无需再次改代码。
**回滚条件**：若引入付费配额或自研代理，可调低 `request_interval` 并移除 key 轮换；若节流逻辑造成不可接受的延迟，需权衡单 key 快速跑 + 429 风险。

## [2025-11-08] Stage 1 Gemini 批次 065-084 覆盖
**背景**：Stage 1 真实解释替换在 000-064 完成后停留一周，WSL 下缺少可用 Python/pip，导致 065+ 无法继续生成。当前目标是恢复 Linux venv、补齐 requests 依赖，并继续用 Gemini 2.5 Flash 跑 20 个 identity。
**操作**：新建 `~/venvs/fyp` 并通过 pip 安装 `pillow`、`httpx`、`requests`，随后按批次运行 `python code/effpp_explain.py --mode chatgpt --chatgpt-provider gemini --chatgpt-model gemini-2.5-flash --chatgpt-request-interval 6.5 --identities 065-084`，为长尾 identity（含 train/val/test 多 split）生成 16×5 ann JSON；网络受限时启用 CLI 升权出口。
**观察**：`data/effpp_ann/*/*/{065..084}/frame_0000.ann.json` 全部显示 `source=api`、`llm_model_id=gemini-2.5-flash`、`llm_active_key_index=0`，说明 9 枚官方 key 未触发轮换；部分 identity（如 069、076）跨 train/val/test 多 split，因此仍需约 8–10 分钟/identity。运行日志多次提示 `Missing original crop ... rank >=16`，但 0–15 均成功落盘。
**影响面**：真实解释覆盖范围扩展到 000-084（85 个 identity），剩余 085-999 保持 placeholder；Stage 1 出口仍需完成余下 915 个 identity 并重跑 schema/QA/指标。WSL 侧 venv 已就绪，可复用命令在后续会话继续跑。
**回滚条件**：若 Gemini 免费额度再次耗尽或外网受限，可回落到 placeholder 版本并等待配额刷新；若 WSL venv 损坏，可重新创建 `~/venvs/fyp` 并复用 `requirements.txt`。
