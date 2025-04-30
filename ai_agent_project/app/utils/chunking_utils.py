# app/utils/chunking_utils.py

from typing import List

def split_text_into_chunks(text: str, max_chunk_size: int = 1500) -> List[str]:
    chunks = []
    current_chunk = ""

    for paragraph in text.split("\n\n"):
        if len(current_chunk) + len(paragraph) < max_chunk_size:
            current_chunk += paragraph + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

async def ask_llm_in_batches(llm, chunks: List[str], system_prompt: str = "Please summarize the following text.") -> str:
    final_response = []

    for idx, chunk in enumerate(chunks):
        user_input = f"{system_prompt}\n\n{chunk}"

        # 注意这里根据你实际调用的 llm 方法稍微调整
        response = await llm.acall(user_input)
        final_response.append(response['content'])  # 你现有返回的是 dict

    return "\n\n".join(final_response)
