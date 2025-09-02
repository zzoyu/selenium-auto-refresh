import os
import time
import pyotp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from decrypt import decrypt_to_secret

# .env 파일에서 사용자 정보 가져오기
from dotenv import load_dotenv
load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
OTP_SECRET = os.getenv("OTP_SECRET")
LOGIN_URL = os.getenv("LOGIN_URL")
SHELL_URL = os.getenv("SHELL_URL")

# OTP Secret 추출
if OTP_SECRET.startswith("otpauth-migration://offline?data="):
    OTP_SECRET = OTP_SECRET.replace("otpauth-migration://offline?data=", "")
    OTP_SECRET = decrypt_to_secret(OTP_SECRET)

# 환경 변수 검증
if not all([USERNAME, PASSWORD, OTP_SECRET, LOGIN_URL, SHELL_URL]):
    missing = [name for name, value in [
        ("USERNAME", USERNAME), ("PASSWORD", PASSWORD), ("OTP_SECRET", OTP_SECRET),
        ("LOGIN_URL", LOGIN_URL), ("SHELL_URL", SHELL_URL)
    ] if not value]
    raise ValueError(f"다음 환경 변수가 설정되지 않았습니다: {', '.join(missing)}")

print("환경 변수 로드 완료:")
print(f"- USERNAME: {USERNAME[:3]}***")
print(f"- LOGIN_URL: {LOGIN_URL}")
print(f"- SHELL_URL: {SHELL_URL}")


# 웹 드라이버 설정
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
# 디버깅을 위한 추가 옵션
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=options)
# 자동화 감지 우회
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

def login():
    """로그인 페이지로 이동하여 아이디, 비밀번호, OTP를 입력하고 로그인합니다."""
    try:
        print(f"초기 접속 URL로 이동합니다: {LOGIN_URL}")
        driver.get(LOGIN_URL)
        
        # 페이지 로딩 대기
        time.sleep(3)
        print(f"현재 URL: {driver.current_url}")

        # 로그인 폼이 로드될 때까지 대기
        print("로그인 폼 로딩을 기다립니다...")
        
        # 다양한 선택자로 아이디 필드 찾기 시도
        print("아이디 입력 필드를 찾습니다...")
        user_field = None
        selectors = [
            (By.NAME, "user"),
            (By.NAME, "userid"),
            (By.NAME, "username"),
            (By.NAME, "id"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.CSS_SELECTOR, "input[placeholder*='아이디']"),
            (By.CSS_SELECTOR, "input[placeholder*='ID']"),
        ]
        
        for selector_type, selector_value in selectors:
            try:
                print(f"시도 중: {selector_type} = '{selector_value}'")
                user_field = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                print(f"아이디 필드를 찾았습니다: {selector_type} = '{selector_value}'")
                break
            except TimeoutException:
                continue
        
        if user_field is None:
            print("아이디 입력 필드를 찾을 수 없습니다.")
            print("사용 가능한 input 요소들:")
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for i, inp in enumerate(inputs):
                inp_type = inp.get_attribute("type") or "text"
                inp_id = inp.get_attribute("id") or "없음"
                inp_name = inp.get_attribute("name") or "없음"
                inp_placeholder = inp.get_attribute("placeholder") or "없음"
                print(f"  {i+1}. type='{inp_type}', id='{inp_id}', name='{inp_name}', placeholder='{inp_placeholder}'")
            return False
        
        user_field.clear()
        user_field.send_keys(USERNAME)
        print("아이디 입력 완료")

        # OTP 입력 (비밀번호 전에 입력)
        print("OTP 입력 단계...")
        try:
            print("OTP 입력 필드를 찾습니다...")
            otp_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "authsms2"))
            )
            print("OTP 입력 필드를 찾았습니다.")
            
            totp = pyotp.TOTP(OTP_SECRET)
            otp_code = totp.now()
            print(f"생성된 OTP: {otp_code}")

            otp_input.clear()
            otp_input.send_keys(otp_code)
            print("OTP를 입력했습니다.")
            
        except TimeoutException:
            print("OTP 입력 필드를 찾지 못했습니다. OTP가 필요하지 않을 수 있습니다.")

        # 비밀번호 입력 필드 찾기 및 입력
        print("비밀번호 입력 필드를 찾습니다...")
        passwd_field = None
        passwd_selectors = [
            (By.NAME, "passwd"),
            (By.NAME, "password"),
            (By.NAME, "pwd"),
            (By.CSS_SELECTOR, "input[type='password']"),
        ]
        
        for selector_type, selector_value in passwd_selectors:
            try:
                print(f"시도 중: {selector_type} = '{selector_value}'")
                passwd_field = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                print(f"비밀번호 필드를 찾았습니다: {selector_type} = '{selector_value}'")
                break
            except TimeoutException:
                continue
        
        if passwd_field is None:
            print("비밀번호 입력 필드를 찾을 수 없습니다.")
            return False
            
        passwd_field.clear()
        passwd_field.send_keys(PASSWORD)
        print("비밀번호 입력 완료")

        # 동의 체크박스 체크
        print("동의 체크박스를 찾습니다...")
        try:
            agree_checkbox = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.NAME, "agree"))
            )
            if not agree_checkbox.is_selected():
                agree_checkbox.click()
                print("동의 체크박스를 체크했습니다.")
            else:
                print("동의 체크박스가 이미 체크되어 있습니다.")
        except TimeoutException:
            print("동의 체크박스를 찾을 수 없습니다.")

        # 로그인 버튼 클릭
        print("로그인 버튼을 찾습니다...")
        login_button = None
        button_selectors = [
            (By.CLASS_NAME, "btn_login"),
        ]
        
        for selector_type, selector_value in button_selectors:
            try:
                print(f"시도 중: {selector_type} = '{selector_value}'")
                login_button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                print(f"로그인 버튼을 찾았습니다: {selector_type} = '{selector_value}'")
                break
            except TimeoutException:
                continue
        
        if login_button is None:
            print("로그인 버튼을 찾을 수 없습니다.")
            print("사용 가능한 button 및 input 요소들:")
            buttons = driver.find_elements(By.TAG_NAME, "button") + driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
            for i, btn in enumerate(buttons):
                btn_text = btn.text or btn.get_attribute("value") or "없음"
                btn_id = btn.get_attribute("id") or "없음"
                btn_class = btn.get_attribute("class") or "없음"
                print(f"  {i+1}. text/value='{btn_text}', id='{btn_id}', class='{btn_class}'")
            return False
            
        login_button.click()
        print("로그인 버튼을 클릭했습니다.")

        # 페이지 변화 대기
        time.sleep(5)
        print(f"로그인 후 현재 URL: {driver.current_url}")

        # 최종 로그인 완료 확인
        print(f"로그인 완료를 확인합니다. 목표 URL: {SHELL_URL}")
        
        # URL이 SHELL_URL로 시작하는지 확인 (완전 일치가 아닌 포함 확인)
        try:
            WebDriverWait(driver, 20).until(
                lambda driver: SHELL_URL in driver.current_url or "shell" in driver.current_url.lower()
            )
            print("로그인에 성공하여 셸 페이지로 이동했습니다.")
            return True
        except TimeoutException:
            print(f"목표 URL로 이동하지 못했습니다. 현재 URL: {driver.current_url}")
            # 수동으로 URL 확인
            if SHELL_URL in driver.current_url or "shell" in driver.current_url.lower():
                print("URL 확인: 셸 페이지로 보입니다. 계속 진행합니다.")
                return True
            # 로그인이 성공했는지 다른 방법으로 확인
            if "auth" not in driver.current_url and "login" not in driver.current_url.lower():
                print("로그인 페이지가 아닌 곳에 있으므로 로그인이 성공한 것으로 판단합니다.")
                return True
            return False

    except TimeoutException as e:
        print(f"로그인 실패: 타임아웃 발생. 현재 URL: {driver.current_url}")
        print(f"오류 상세 정보: {e}")
        return False
    except Exception as e:
        print(f"로그인 중 예상치 못한 오류 발생: {e}")
        return False

def refresh_and_handle_alert():
    """연장(새로고침) 버튼을 누르고 JavaScript 확인 창을 자동으로 닫습니다."""
    while True:
        try:
            print("연장 버튼 클릭을 시도합니다...")
            # value="연장"인 input 버튼을 찾습니다
            refresh_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='button'][value='연장']"))
            )
            refresh_button.click()
            print("연장 버튼을 클릭했습니다.")

            print("확인 창(alert)을 기다립니다...")
            WebDriverWait(driver, 10).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"확인 창 발견: '{alert_text}'")
            alert.accept()
            print("확인 창을 자동으로 닫았습니다.")

            print("20분 동안 대기합니다...")
            time.sleep(20*60)  # 20분 대기

        except TimeoutException:
            print("연장 버튼 또는 확인 창을 찾는 데 실패했습니다.")
            print("로그인 상태를 확인하고, 필요한 경우 다시 로그인을 시도합니다.")
            if driver.current_url != SHELL_URL:
                if not login():
                    print("재로그인에 실패하여 프로그램을 종료합니다.")
                    break
            else:
                print("이미 셸 페이지에 있으므로 연장을 다시 시도합니다.")

        except NoAlertPresentException:
            print("처리할 확인 창이 없습니다.")
        except Exception as e:
            print(f"연장 작업 중 예상치 못한 오류 발생: {e}")
            break

if __name__ == "__main__":
    if login():
        print(f"로그인 성공. {SHELL_URL} 페이지의 20분 간격 자동 연장을 시작합니다.")
        refresh_and_handle_alert()
    else:
        print("로그인에 실패하여 프로그램을 종료합니다.")