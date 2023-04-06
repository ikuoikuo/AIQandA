import streamlit as st
import openai
from io import StringIO

openai.api_key = "あなたのopenAIのAPIキーを入力してください"
def txt_to_chunks(text, chunk_size=2500) -> list:
    """
    テキストを読み込んで、3000文字を超えないように
    テキストを分割し、リストに格納して返す

    Args:
        txt_path (str): 分割するtxtファイルのパス

    Returns:
        list[str]: 2500文字を超えないように分割されたテキストが格納されたリスト
    """
    chunks = []
    text_length = len(text)

    # テキストをchunk_sizeで分割する
    for i in range(0, text_length, chunk_size):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)

    return chunks

def completion(new_message_text:str, settings_text:str = '', past_messages:list = []):
    """
    OpenAIのChatGPT API(gpt-3.5-turbo)を使用して、新しいメッセージテキスト、オプションの設定テキスト、
    過去のメッセージのリストを入力として受け取り、レスポンスメッセージを生成するために使用。

    Args:
    new_message_text (str): モデルがレスポンスメッセージを生成するために使用する新しいメッセージテキスト。
    settings_text (str, optional): 過去のメッセージリストにシステムメッセージとして追加されるオプションの設定テキスト。デフォルトは''です。
    past_messages (list, optional): モデルがレスポンスメッセージを生成するために使用するオプションの過去のメッセージのリスト。デフォルトは[]です。

    Returns:
    tuple: レスポンスメッセージテキストと、新しいメッセージとレスポンスメッセージを追加した過去のメッセージリストを含むタプル。
    """
    if len(past_messages) == 0 and len(settings_text) != 0:
        system = {"role": "system", "content": settings_text}
        past_messages.append(system)
    new_message = {"role": "user", "content": new_message_text}
    past_messages.append(new_message)

    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=past_messages,
        max_tokens=512
    )
    response_message = {"role": "assistant", "content": result.choices[0].message.content}
    past_messages.append(response_message)
    response_message_text = result.choices[0].message.content
    return response_message_text, past_messages

# 要約
def summarize(target_text):
    system_text = "あなたは要約システムです。与えられた文章に対して要約を行ってください。"
    summary, _ = completion(target_text, system_text, [])
    return summary

# 要約QA
def summary_qa(summarized_text, question):
    system_text = "あなたは参考文章をもとに質問に回答するシステムです。参考文章をもとに、段階的に考えて論理的に回答してください。"
    question_prompt = f"""## 参考文章

{summarized_text}

## 質問

{question}"""
    answer, _ = completion(question_prompt, system_text, [])
    return answer


st.title("AI Q&A")
st.header('テキストファイルの内容をもとにQ&Aを行うことができます')
#ファイルアップロード
uploaded_file = st.file_uploader("ファイルアップロード", type='txt',accept_multiple_files= False)
if uploaded_file is not None:
    st.write('テキストを読み込んでいます...')
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    text = stringio.read()
    chunked_text = txt_to_chunks(text)
    # 分割された文章をそれぞれ要約する
    summarized_texts = []
    for part_text in chunked_text:
        summary = summarize(part_text)
        summarized_texts.append(summary)
    summarized_text_str = "\n".join(summarized_texts)
    st.write('完了しました')

# 要約された文章でQAする
question = st.text_input("質問を入力してください", "")
if st.button("送信"):
    st.write('考え中です...')
    answer = summary_qa(summarized_text_str[:2500], question)
    st.markdown(answer)
