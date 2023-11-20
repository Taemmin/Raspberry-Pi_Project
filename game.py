import random
import pygame
import spidev
import time
import sys
import RPi._GPIO as GPIO
import threading

# 초기화
pygame.init()
GPIO.setmode(GPIO.BCM)

# 부저 관련 설정
buzzer_pin = 18
GPIO.setup(buzzer_pin, GPIO.OUT)
buzzer = GPIO.PWM(buzzer_pin, 1)

# 화면 설정
screen_width = 300
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("무궁화 꽃이 피었습니다")

# 색상 정의
white = (255, 255, 255)
blue = (0, 0, 255)
black = (0, 0, 0)

# 버튼 관련 설정
start_button_rect = pygame.Rect(100, 250, 100, 50)
start_button_color = (0, 255, 0)
start_button_text = pygame.font.Font(None, 36).render("Start", True, white)
start_button_text_rect = start_button_text.get_rect(center=start_button_rect.center)

# 조이스틱 관련 설정
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 100000

sw_channel = 0
vrx_channel = 1
vry_channel = 2

xZero = 507
yZero = 523
tolerancevalue = 10

global buzzer_check
buzzer_check = False


def position(adcnum, zerovalue):
    return readadc(adcnum) - zerovalue


def readadc(adcnum):
    if adcnum > 7 or adcnum < 0:
        return -1
    r = spi.xfer2([1, (8 + adcnum) << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data


move = 0

# 이미지 로드
ball_image = pygame.image.load("character2.jpg")
ball_image = pygame.transform.scale(ball_image, (100, 100))

ball2_image = pygame.image.load("sand.jpg")
ball2_image = pygame.transform.scale(ball2_image, (screen_width, screen_height))

ball3_image = pygame.image.load("character3.jpg")
ball3_image = pygame.transform.scale(ball3_image, (100, 100))

ball4_image = pygame.image.load("heart1.jpg")
ball4_image = pygame.transform.scale(ball4_image, (30, 30))

ball5_image = pygame.image.load("heart1.jpg")
ball5_image = pygame.transform.scale(ball5_image, (30, 30))

ball6_image = pygame.image.load("heart1.jpg")
ball6_image = pygame.transform.scale(ball6_image, (30, 30))


frq = [330, 440, 440, 440, 392, 440, 440, 330, 330, 392]


def timer_event():
    print("타이머 이벤트 발생!")
    play_buzzer(frq)
    timer = threading.Timer(5, timer_event)
    timer.start()


# 부저 울리기 함수
def play_buzzer(frq):
    global buzzer_check
    buzzer_check = True
    print("play_buzzer True")
    buzzer.start(25)
    for fr in frq:
        buzzer.ChangeFrequency(fr)
        time.sleep(0.3)
    buzzer.stop()
    buzzer_check = False
    print("play_buzzer False")


# 초기 화면 그리기
screen.fill(white)
pygame.draw.rect(screen, start_button_color, start_button_rect)
screen.blit(start_button_text, start_button_text_rect)
pygame.display.flip()

# 게임 루프
running = True
move_circle = False  # 조이스틱 움직임 활성화 여부
yPos_normalized = 0  # 초기화
line_y = screen_height // 2 + 260  # 중간 가로 줄의 y 좌표값 계산
timer = 0

prev_ypos = 0

count = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif (
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        ):  # 마우스 왼쪽 버튼 누를 때
            # buzzer.start(25)
            play_buzzer(frq)
            # buzzer.stop()
            if (
                start_button_rect.collidepoint(event.pos) and not move_circle
            ):  # 스타트 버튼을 누르면 조이스틱 움직임 활성화
                start_button_rect.width = 0  # 스타트 버튼 숨기기
                move_circle = True

                timer = threading.Timer(5, timer_event)
                timer.start()

    if move_circle:
        # 조이스틱 값 읽어오기
        yPos = position(vry_channel, yZero)

        # 좌표 변환 (-1 ~ 1 범위)
        yPos_normalized = max(yPos / 512, 0)  # 움직임을 위로만 허용함 (0 또는 양수)
        yPos_normalized = min(yPos_normalized, 1)  # 움직임을 아래로만 허용함 (0 또는 음수)

        y = line_y - int(
            yPos_normalized * (line_y - (screen_height // 2)) * 2
        )  # 원의 시작점을 중간 위로도 움직일 수 있게 조정

        if y < 100:
            move += 10
        if move >= screen_height - 130:
            # "성공하셨습니다!" 메시지 표시
            success_text = pygame.font.SysFont("undotum", 36).render(
                "성공하셨습니다!", True, black
            )
            success_text_rect = success_text.get_rect(
                center=(screen_width // 2, screen_height // 2)
            )
            screen.blit(success_text, success_text_rect)
            pygame.display.flip()
            pygame.time.delay(2000)  # 2초 동안 메시지 표시

        # 화면 초기화
        screen.blit(ball2_image, (0, 0))
        # screen.fill(white)
        pygame.draw.line(screen, black, (0, line_y), (screen_width, line_y))

        # 왼쪽 상단에 heart 이미지 추가
        ball4_rect = ball4_image.get_rect(topleft=(0, 0))
        screen.blit(ball4_image, ball4_rect)

        ball5_rect = ball5_image.get_rect(topleft=(30, 0))
        screen.blit(ball5_image, ball5_rect)

        ball6_rect = ball6_image.get_rect(topleft=(60, 0))
        screen.blit(ball6_image, ball6_rect)

        # 이미지 표시
        ball_rect = ball_image.get_rect(midtop=(screen_width // 2, 0))
        screen.blit(ball_image, ball_rect)

        # 이미지 업데이트
        if buzzer_check == False:
            ball_rect = ball_image.get_rect(
                midtop=(screen_width // 2, 0)
            )  # 부저가 울리지 않을 때
            screen.blit(ball_image, ball_rect)
        else:
            ball3_rect = ball3_image.get_rect(midtop=(screen_width // 2, 0))  # 부저가 울릴 때
            screen.blit(ball3_image, ball3_rect)

        if prev_ypos != yPos_normalized:  # 움직였을 때
            prev_ypos = yPos_normalized

            if buzzer_check == False:
                pygame.draw.circle(
                    screen, blue, (screen_width // 2, screen_height - 20), 20
                )
                move = 0

            else:
                pygame.draw.circle(
                    screen, blue, (screen_width // 2, screen_height - move - 20), 20
                )
        else:
            pygame.draw.circle(
                screen, blue, (screen_width // 2, screen_height - move - 20), 20
            )

    # 화면 업데이트
    pygame.display.flip()
    pygame.time.delay(200)  # 50ms 딜레이


# 게임 종료
pygame.quit()
GPIO.cleanup()  # GPIO 정리
sys.exit()
