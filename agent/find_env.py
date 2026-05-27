import subprocess
import sys

envs = ["base", "LLM", "MetaGpt", "Qwen-7B-Chat", "RA_MOA", "RL", "StateProve", "ai_agent", "camel", "claude_agent", "csac_lora", "deepagent", "deepgrncs", "deepsearch", "ft_rag", "hug_LLM", "image_pro", "image_process", "langgraph", "langgraph_study", "llamaIndex_study", "llamaindex", "llm_train", "meta_llama", "nanogpt", "nlp", "script_train", "test"]

print("Scanning conda environments...")
for env in envs:
    cmd = f"conda run -n {env} python -c \"import langchain_openai, langchain_milvus; print('FOUND')\""
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if "FOUND" in res.stdout:
            print(f"🎉 FOUND pre-configured packages in conda env: {env}")
            sys.exit(0)
        else:
            print(f" - {env}: not matching")
    except subprocess.TimeoutExpired:
        print(f" - {env}: timeout")
    except Exception as e:
        print(f" - {env}: error {e}")

print("Scanning completed. No environment found.")
