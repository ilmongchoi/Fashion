#유틸리티 함수: 웹 애플리케이션의 핵심 로직이 아니라 보조 기능을 담당하는 함수들을 구현하는 용도
#app.py파일과 분리 이유: 코드의 가독성과 유지보수성 향상
#chatgpt api 통신 함수, dall-e 이미지 생성 함수

import openai
import requests
from PIL import Image
from io import BytesIO

# 설정 변수
OPENAI_API_KEY = "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"
MODEL_NAME = "gpt-3.5-turbo"

class ChatGPT:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key
    
    #클라이언트 메시지 받아 옷 추천 응답 함수
    def chat_first_message(self, query):
        #대화 메시지 목록 생성
        messages = [
            {"role": "system", "content": "You are a fashion expert and assistant who recommends clothes to users based on their preferences."},
            {"role": "user", "content": query}
        ]
        
        #ChatGPT 모델에 대화 메시지 전달하여 응답 받기
        response = openai.ChatCompletion.create(model=self.model, messages=messages)
        answer = response['choices'][0]['message']['content']
        
        return answer#응답 반환

    # #<<응답 결과를 명사화 형용사로 압축하는 함수>>-결국 사용X
    # def chat_second_message(self, previous_answer):
    #     messages = [
    #         {"role": "system", "content": "You are a fashion expert and assistant who recommends clothes to users based on their preferences."},
    #         {"role": "user", "content": "Condense up to 4 outward description to focus on nouns and adjectives separated by ,"},
    #         {"role": "user", "content": previous_answer}
    #     ]
        
    #     response = openai.ChatCompletion.create(model=self.model, messages=messages)
    #     answer = response['choices'][0]['message']['content']
        
    #     return answer

    #번역 함수
    def translate(self, text):
        # 번역을 위한 메시지 설정
        messages = [
            {"role": "system", "content": "You are a helpful assistant who is good at translating."},
            {"role": "assistant", "content": text},
            {"role": "user", "content": "Please translate it naturally into Korean if it's English and English if it's Korean."}
        ]
        # ChatGPT API 호출하여 번역된 텍스트 받기
        response = openai.ChatCompletion.create(model=self.model, messages=messages)
        translated_text = response['choices'][0]['message']['content']
        return translated_text
    
    #요약 함수
    def summarize_text(self, text):
        # ChatGPT API 호출을 위한 메시지 설정
        messages = [
            {"role": "assistant", "content": text},
            {"role": "user", "content": "Please answer within 160 tokens"}
        ]
        # ChatGPT API를 사용하여 텍스트 요약 수행
        response = openai.ChatCompletion.create(model=self.model, messages=messages)
        summarized_text = response['choices'][0]['message']['content']
        return summarized_text

class ImageGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key

    #이미지 생성 함수
    def generate_image(self, prompt):
        # 이미지 생성 요청을 위해 OpenAI API 호출
        response = openai.Image.create(prompt=prompt, n=3, size="1024x1024")

        image_urls = []
        # 각 이미지 URL 저장
        for data in response['data']:
            image_urls.append(data['url'])

        return image_urls

        # #<<이미지 정상 생성 여부 확인 코드>>
        #  # 각 이미지 URL에 GET 요청 보내기
        # for data in response['data']:
        #     image_url = data['url']
        #     res = requests.get(image_url)
        #     # 응답 받은 이미지 데이터를 PIL Image로 열기
        #     img = Image.open(BytesIO(res.content))
        #     # 이미지 출력
        #     img.show()

    def generate_prompt(self, answer):
        prompt = f"{answer} Please create a customized clothing recommendation image for the article."
        return prompt
    
#<<기능 테스트 위한 코드들>>--------------------------------------------------------------------
# # ChatGPT 인스턴스 생성
# chat_gpt = ChatGPT(OPENAI_API_KEY, MODEL_NAME)

# # ImageGenerator 인스턴스 생성
# image_generator = ImageGenerator(OPENAI_API_KEY)

# # 질문 작성 및 ChatGPT와 대화하여 응답 받기
# query = "What clothes would you recommend for a summer party?"#사용자 맞춤 질문으로 설정
# answer = chat_gpt.chat(query)
# print(answer)

# # 영어로 번역하기
# translated_text = chat_gpt.translate_to_english(answer)
# print(translated_text)

# # 프롬프트 생성 및 이미지 생성
# prompt = image_generator.generate_prompt(answer)
# print(prompt)
# image_generator.generate_image(prompt)
#-------------------------------------------------------------------------------------------------
