# <flask 애플리케이션 구현: 애플리케이션 핵심 로직 구현>
# <웹 요청 처리, 데이터 반환 기능>

# <아래는 작성할 코드 내용 명시>
# 필요한 모듈 import: Flask, render_template, request 등의 모듈
from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from utils import ImageGenerator, ChatGPT

# Flask 애플리케이션 생성: Flask 객체를 생성하고, 애플리케이션을 초기화
app = Flask(__name__)

# 설정 변수
OPENAI_API_KEY = "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"
MODEL_NAME = "gpt-3.5-turbo"

#날씨 정보 크롤링 함수
def get_weather_data():
    url = 'https://weather.naver.com/today/15200330'  # 아산시 탕정면 URL
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    weather = soup.select_one('strong.current')  # 현재 날씨
    location = soup.select_one('strong.location_name')  # 위치
    weatherstatus = soup.select_one('span.weather')  # 날씨 상태
    temperature = soup.select_one('strong.temperature')  # 기온
    min_temperature = soup.select_one('.temperature span.lowest')  # 최저 기온
    max_temperature = soup.select_one('.temperature span.highest')  # 최고 기온

    # 날씨 상태 영어 번역 함수
    translate_weather_status = {
        '맑음': 'Clear',
        '구름 조금': 'Partly Cloudy',
        '구름 많음': 'Mostly Cloudy',
        '흐림': 'Cloudy',
        '비': 'Rain',
        '비/눈': 'Rain/Snow',
        '눈': 'Snow',
        '소나기': 'Shower',
        '천둥번개': 'Thunderstorm',
        '황사': 'Yellow Dust',
        '연기': 'Smoke',
        '대체로 흐림': 'Mostly Cloudy'
        #네이버 날씨에서 날씨상태로 나올 수 있는 경우 수
    }
    weather_status_english = translate_weather_status.get(weatherstatus.get_text(strip=True), weatherstatus.get_text(strip=True))
    # 질문 프롬프트 생성
    query = f"What clothes would you recommend for today's weather? The current temperature is {weather.get_text(strip=True).replace('현재 온도', '')} with a forecast of { weather_status_english}. The expected range is {min_temperature.get_text(strip=True).replace('최저기온', '')} to {max_temperature.get_text(strip=True).replace('최고기온', '')}."

    return {
        'query': query,
        'weather':weather.get_text(strip=True).replace('현재 온도', ''),
        'location': location.get_text(strip=True),
        'weatherstatus': weatherstatus.get_text(strip=True),
        'temperature': temperature.get_text(strip=True),
        'min_temperature': min_temperature.get_text(strip=True),
        'max_temperature': max_temperature.get_text(strip=True)
    }

# 각 URL에 해당하는 라우트와 뷰 함수를 작성
# 각 뷰 함수는 해당 페이지의 HTML 템플릿 파일 렌더링하고 필요 데이터 전달
# 각 뷰 함수는 해당 페이지 동작 구현
# 개인 옷 추천 페이지의 뷰 함수는 사용자 입력을 처리하고 ChatGPT API와 통신하여 추천 결과 얻어옴

@app.route('/')
def home():
    # 홈 화면을 렌더링
    return render_template('MainWeb.html')

# 날씨 맞춤 옷 추천 경로에 대한 요청 처리
@app.route('/weather')
def weather():
    # 날씨 정보 페이지 렌더링
    weather_data = get_weather_data()  # 날씨 정보를 가져오는 함수 호출
    
     # ChatGPT 인스턴스 생성
    chat_gpt = ChatGPT(OPENAI_API_KEY, MODEL_NAME)

    # ChatGPT와 대화하여 응답 받기
    query = weather_data['query']  # 질문 데이터 가져오기
    answer1 = chat_gpt.chat_first_message(query)  # ChatGPT를 사용하여 질문 전달 및 응답 받기
    answer1_korea = chat_gpt.translate(answer1) #사용자에게 보여주기 위해 한국어로 번역
    print("gpt응답1: "+answer1_korea)

    # ImageGenerator 인스턴스 생성
    image_generator = ImageGenerator(OPENAI_API_KEY)
    
    # 프롬프트 생성
    prompt = image_generator.generate_prompt(answer1)
    print("이미지 생성 질문: "+prompt)

    try: 
        # 이미지 생성
        image_urls = image_generator.generate_image(prompt)
    except Exception as e:
        print("예외 발생:", e)# 질문문 너무 길 경우 오류발생
        answer2 = chat_gpt.summarize_text(answer1) # 글 요약
        print("글 요약 : "+answer2)
        # 프롬프트 생성
        prompt = image_generator.generate_prompt(answer2)
        print("이미지 생성 질문: "+prompt)
        # 이미지 생성
        image_urls = image_generator.generate_image(prompt)
        print("예외 처리 완료")

    return render_template('weather.html', weather=weather_data, answer1_korea = answer1_korea, image_urls=image_urls)

# 개인 맞춤 옷 추천 경로에 대한 요청 처리
# 사용자 요청 처리:
# Flask에서 사용자 요청 데이터 받아오고 필요한 처리 수행 위해 request 객체 활용
# 예) POST 요청으로 전달된 사용자 입력을 request.form을 통해 가져옴
@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        # 콤보박스에서 선택한 데이터 가져오기
        personal_color = request.form.get("personal-color")
        color = request.form.get("color")
        fashion_style = request.form.get("fashion-style")
        season = request.form.get("season")
        gender = request.form.get("gender")

        # 가져온 데이터 콘솔에 출력
        print("Personal Color:", personal_color)
        print("Color:", color)
        print("Fashion Style:", fashion_style)
        print("Season:", season)
        print("Gender:", gender)

        # ChatGPT 인스턴스 생성
        chat_gpt = ChatGPT(OPENAI_API_KEY, MODEL_NAME)

        # ChatGPT와 대화하여 응답 받기
        # 받아온 사용자 데이터 컬러, 퍼스널컬러 두 경우로 나누어 질문 생성
        if not color:
            query = f"Could you recommend {gender}'s autumn fashion with a {fashion_style} style, while considering the {personal_color} personal color palette? Please answer within 160 tokens"
        else:
            query = f"Could you please recommend {gender}'s autumn fashion with a {fashion_style} style incorporating {color} color? Please answer within 200 tokens"
        print("요청질문: " + query)

        answer1 = chat_gpt.chat_first_message(query)  # ChatGPT를 사용하여 질문 전달 및 응답 받기
        print("gpt응답 : "+answer1)
        answer1_korea = chat_gpt.translate(answer1) #한국어로 번역
        print("gpt응답 한국어로 : "+answer1_korea)

        # ImageGenerator 인스턴스 생성
        image_generator = ImageGenerator(OPENAI_API_KEY)
        
        # 프롬프트 생성
        prompt = image_generator.generate_prompt(answer1)
        print("이미지 생성 질문: "+prompt)

        try: 
            # 이미지 생성
            image_urls = image_generator.generate_image(prompt)
        except Exception as e:
            print("예외 발생:", e)# 질문문이 너무 긴 경우
            answer2 = chat_gpt.summarize_text(answer1) # 글 요약
            print("글 요약 : "+answer2)
            # 프롬프트 생성
            prompt = image_generator.generate_prompt(answer2)
            print("이미지 생성 질문: "+prompt)
            # 이미지 생성
            image_urls = image_generator.generate_image(prompt)
            print("예외 처리 완료")

        return render_template('Findstyle.html', answer1_korea = answer1_korea, image_urls = image_urls) #옷 추천 글, 이미지 값 반환
    
    else:# 사용자 정보 수신을 하지 못할 경우
        # 개인 옷 추천 페이지를 렌더링
        return render_template('recommend.html')

## <<Findstyle 웹 페이지 테스트 코드>>
# @app.route('/Findstyle')
# def findstyle():
#     return render_template('Findstyle.html')

# Flask 애플리케이션 실행
# app.run() 메서드 호출로 Flask 애플리케이션 실행. Flask는 내장 서버를 사용하여 애플리케이션 실행 가능. 기본 로컬 호스트 5000번 포트에서 실행.
if __name__ == '__main__':
    app.run()
