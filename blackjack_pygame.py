import pygame
import sys
import random
import os

# ======== 1. 核心邏輯與資料管理 ========

def load_player_data(filename="players.txt"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    players = {}
    if not os.path.exists(filepath):
        return players
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(',')
                    if len(parts) >= 4:
                        players[parts[0]] = {
                            'money': int(parts[1]),
                            'total': int(parts[2]),
                            'wins': int(parts[3]),
                            'win_rate': parts[4] if len(parts) > 4 else "0.0%"
                        }
    except Exception:
        pass
    return players

def save_player_data(players, filename="players.txt"):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            for name, data in players.items():
                if data['total'] > 0:
                    win_rate = (data['wins'] / data['total']) * 100
                    win_rate_str = f"{win_rate:.1f}%"
                else:
                    win_rate_str = "0.0%"
                line = f"{name},{data['money']},{data['total']},{data['wins']},{win_rate_str}\n"
                file.write(line)
    except Exception as e:
        print(f"存檔錯誤: {e}")

def create_deck():
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    deck = [(s, r) for s in suits for r in ranks]
    random.shuffle(deck)
    return deck

def get_card_value(card):
    suit, rank = card
    if rank in ['J', 'Q', 'K']:
        return 10
    elif rank == 'A':
        return 11
    else:
        return int(rank)

def calculate_hand_value(cards):
    value = sum(get_card_value(card) for card in cards)
    aces = sum(1 for card in cards if card[1] == 'A')
    while value > 21 and aces > 0:
        value -= 10
        aces -= 1
    return value

# ======== 2. Pygame 視覺與介面設定 ========

# 初始化 Pygame
pygame.init()

# 設定常數
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
CARD_WIDTH = 100
CARD_HEIGHT = 140
FPS = 60

# 顏色定義 (RGB)
COLOR_BG = (34, 139, 34)      # 賭桌綠
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (220, 20, 60)
COLOR_GRAY = (200, 200, 200)
COLOR_BUTTON = (50, 50, 50)
COLOR_BUTTON_HOVER = (70, 70, 70)
COLOR_SHADOW = (20, 20, 20)   # 卡牌陰影

# 字型設定 (強力修復中文顯示問題)
def get_chinese_font(size):
    """
    針對 Windows 系統強制讀取微軟正黑體
    """
    # Windows 常見的中文字型路徑
    font_paths = [
        "C:\\Windows\\Fonts\\msjh.ttc",   # 微軟正黑體 (Win10/11)
        "C:\\Windows\\Fonts\\msjh.ttf",   # 舊版路徑
        "C:\\Windows\\Fonts\\simhei.ttf", # 黑體
        "C:\\Windows\\Fonts\\mingliu.ttc" # 細明體
    ]
    
    # 1. 先試試看絕對路徑 (最穩)
    for path in font_paths:
        if os.path.exists(path):
            return pygame.font.Font(path, size)
            
    # 2. 如果都沒有，試試看系統自動搜尋
    try:
        font_path = pygame.font.match_font("microsoftyahei")
        if font_path:
            return pygame.font.Font(font_path, size)
    except:
        pass

    # 3. 真的沒辦法了，回傳預設 (中文會變框框)
    print("警告：找不到中文字型，將使用預設字型")
    return pygame.font.Font(None, size)

# 初始化字型變數
FONT_LARGE = get_chinese_font(48)
FONT_MEDIUM = get_chinese_font(32)
FONT_SMALL = get_chinese_font(24)

# 卡牌上的數字使用系統預設字型 (因為只需要顯示英文和數字)
try:
    FONT_CARD = pygame.font.SysFont("arial", 28, bold=True)
except:
    FONT_CARD = pygame.font.Font(None, 28)

# 按鈕類別
class Button:
    def __init__(self, text, x, y, width, height, action_code):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action_code = action_code
        self.is_hovered = False

    def draw(self, screen):
        color = COLOR_BUTTON_HOVER if self.is_hovered else COLOR_BUTTON
        # 畫按鈕背景
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_WHITE, self.rect, 2, border_radius=10) # 邊框
        
        # 畫文字
        text_surf = FONT_MEDIUM.render(self.text, True, COLOR_WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

# 遊戲主程式類別
class BlackjackGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Python Blackjack - Pygame 版")
        self.clock = pygame.time.Clock()
        
        self.players = load_player_data()
        self.current_player_name = ""
        
        # 遊戲狀態: LOGIN, BETTING, PLAYING, RESULT
        self.state = "LOGIN"
        
        # 輸入框變數
        self.input_text = ""
        
        # 遊戲變數
        self.player_hand = []
        self.dealer_hand = []
        self.deck = []
        self.bet = 0
        self.message = ""
        
        # 按鈕群組
        self.buttons = []

    def init_buttons(self):
        self.buttons = []
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT - 100
        
        if self.state == "LOGIN":
            self.buttons.append(Button("確認登入", cx - 75, cy, 150, 50, "LOGIN_CONFIRM"))
            
        elif self.state == "BETTING":
            self.buttons.append(Button("下注 $10", cx - 160, cy, 150, 50, "BET_10"))
            self.buttons.append(Button("下注 $50", cx + 10, cy, 150, 50, "BET_50"))
            self.buttons.append(Button("重置", cx - 75, cy + 60, 150, 40, "BET_RESET"))
            self.buttons.append(Button("發牌 (Deal)", cx - 75, cy - 60, 150, 50, "DEAL"))

        elif self.state == "PLAYING":
            self.buttons.append(Button("要牌 (Hit)", cx - 160, cy, 150, 50, "HIT"))
            self.buttons.append(Button("停牌 (Stand)", cx + 10, cy, 150, 50, "STAND"))

        elif self.state == "RESULT":
            self.buttons.append(Button("再玩一局", cx - 75, cy, 150, 50, "RESTART"))
            self.buttons.append(Button("離開遊戲", cx - 75, cy + 60, 150, 40, "QUIT"))

    def draw_card(self, card, x, y, hidden=False):
        # 畫陰影
        shadow_rect = pygame.Rect(x + 5, y + 5, CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_SHADOW, shadow_rect, border_radius=8)

        card_rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

        if hidden:
            # 畫卡背
            pygame.draw.rect(self.screen, (139, 0, 0), card_rect, border_radius=8) 
            pygame.draw.rect(self.screen, COLOR_WHITE, card_rect, 2, border_radius=8) 
            pygame.draw.line(self.screen, (255,215,0), (x+10, y+10), (x+CARD_WIDTH-10, y+CARD_HEIGHT-10), 2)
            pygame.draw.line(self.screen, (255,215,0), (x+CARD_WIDTH-10, y+10), (x+10, y+CARD_HEIGHT-10), 2)
            return

        # 畫卡面
        pygame.draw.rect(self.screen, COLOR_WHITE, card_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_BLACK, card_rect, 1, border_radius=8)

        suit, rank = card
        color = COLOR_RED if suit in ['♥', '♦'] else COLOR_BLACK
        
        # 左上角數字
        rank_surf = FONT_CARD.render(rank, True, color)
        suit_surf = FONT_CARD.render(suit, True, color)
        self.screen.blit(rank_surf, (x + 5, y + 5))
        self.screen.blit(suit_surf, (x + 5, y + 30))
        
        # 中央大花色
        try:
            large_suit_font = pygame.font.SysFont("arial", 60)
            large_suit = large_suit_font.render(suit, True, color)
        except:
            large_suit = FONT_MEDIUM.render(suit, True, color)
            
        text_rect = large_suit.get_rect(center=card_rect.center)
        self.screen.blit(large_suit, text_rect)

        # 右下角數字
        rank_rect = rank_surf.get_rect(bottomright=(x + CARD_WIDTH - 5, y + CARD_HEIGHT - 5))
        self.screen.blit(rank_surf, rank_rect)

    def draw_game_area(self):
        # 1. 顯示玩家資訊
        player_data = self.players.get(self.current_player_name, {'money': 0, 'win_rate': '0%'})
        info_text = f"玩家: {self.current_player_name}  |  籌碼: ${player_data['money']}  |  本局下注: ${self.bet}"
        info_surf = FONT_MEDIUM.render(info_text, True, (255, 215, 0))
        self.screen.blit(info_surf, (20, 20))

        # 2. 畫莊家區域
        dealer_text = FONT_MEDIUM.render("莊家手牌", True, COLOR_WHITE)
        self.screen.blit(dealer_text, (50, 100))
        
        for i, card in enumerate(self.dealer_hand):
            is_hidden = (self.state == "PLAYING" and i == 1)
            self.draw_card(card, 50 + i * 110, 140, hidden=is_hidden)
            
        if self.state == "RESULT":
             score_text = f"點數: {calculate_hand_value(self.dealer_hand)}"
             self.screen.blit(FONT_SMALL.render(score_text, True, COLOR_GRAY), (50, 290))

        # 3. 畫玩家區域
        player_text = FONT_MEDIUM.render("您的手牌", True, COLOR_WHITE)
        self.screen.blit(player_text, (50, 400))
        
        for i, card in enumerate(self.player_hand):
            self.draw_card(card, 50 + i * 110, 440)
            
        if self.player_hand:
            p_score = calculate_hand_value(self.player_hand)
            score_text = f"點數: {p_score}"
            self.screen.blit(FONT_SMALL.render(score_text, True, COLOR_GRAY), (50, 590))

        # 4. 顯示訊息
        if self.message:
            msg_surf = FONT_LARGE.render(self.message, True, (255, 255, 0))
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            
            bg_rect = msg_rect.inflate(20, 20)
            pygame.draw.rect(self.screen, (0,0,0, 180), bg_rect, border_radius=10)
            self.screen.blit(msg_surf, msg_rect)

    def handle_login(self):
        title = FONT_LARGE.render("BLACKJACK 21點", True, (255, 215, 0))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        prompt = FONT_MEDIUM.render("請輸入您的姓名:", True, COLOR_WHITE)
        self.screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, 250))
        
        input_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 300, 200, 40)
        pygame.draw.rect(self.screen, COLOR_WHITE, input_rect)
        pygame.draw.rect(self.screen, COLOR_BLACK, input_rect, 2)
        
        name_surf = FONT_MEDIUM.render(self.input_text, True, COLOR_BLACK)
        self.screen.blit(name_surf, (input_rect.x + 10, input_rect.y + 5))

    def perform_login(self):
        """執行登入動作"""
        if self.input_text:
            name = self.input_text
            self.current_player_name = name
            if name not in self.players:
                self.players[name] = {'money': 100, 'total': 0, 'wins': 0, 'win_rate': '0.0%'}
            self.input_text = ""
            self.bet = 0
            self.state = "BETTING"
            self.init_buttons()

    def run(self):
        self.init_buttons()
        
        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # 文字輸入處理
                if event.type == pygame.KEYDOWN:
                    if self.state == "LOGIN":
                        if event.key == pygame.K_RETURN:
                            self.perform_login()
                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        else:
                            if len(self.input_text) < 10:
                                self.input_text += event.unicode
                                
                # 按鈕點擊處理
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        for btn in self.buttons:
                            if btn.is_clicked(mouse_pos):
                                self.handle_action(btn.action_code)

            for btn in self.buttons:
                btn.check_hover(mouse_pos)

            self.screen.fill(COLOR_BG)

            if self.state == "LOGIN":
                self.handle_login()
            else:
                self.draw_game_area()

            for btn in self.buttons:
                btn.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

    def handle_action(self, code):
        # [修復重點] 先處理登入，避免存取尚未存在的玩家名稱
        if code == "LOGIN_CONFIRM":
            self.perform_login()
            return  # 重要: 這裡必須 return，否則下面會報錯

        # 讀取玩家資料 (現在確保安全了)
        player_data = self.players[self.current_player_name]
        
        if code == "BET_10":
            if player_data['money'] >= self.bet + 10:
                self.bet += 10
        elif code == "BET_50":
            if player_data['money'] >= self.bet + 50:
                self.bet += 50
        elif code == "BET_RESET":
            self.bet = 0
            
        elif code == "DEAL":
            if self.bet < 10:
                self.message = "最少下注 $10"
                return
            if self.bet > player_data['money']:
                self.message = "資金不足"
                return
            
            self.message = ""
            self.deck = create_deck()
            self.player_hand = [self.deck.pop(), self.deck.pop()]
            self.dealer_hand = [self.deck.pop(), self.deck.pop()]
            self.state = "PLAYING"
            self.init_buttons()
            
            if calculate_hand_value(self.player_hand) == 21:
                self.game_over(player_blackjack=True)

        elif code == "HIT":
            self.player_hand.append(self.deck.pop())
            if calculate_hand_value(self.player_hand) > 21:
                self.game_over(winner="Dealer")

        elif code == "STAND":
            while calculate_hand_value(self.dealer_hand) < 17:
                self.dealer_hand.append(self.deck.pop())
            
            p_val = calculate_hand_value(self.player_hand)
            d_val = calculate_hand_value(self.dealer_hand)
            
            if d_val > 21:
                self.game_over(winner="Player")
            elif p_val > d_val:
                self.game_over(winner="Player")
            elif p_val < d_val:
                self.game_over(winner="Dealer")
            else:
                self.game_over(winner="Tie")

        elif code == "RESTART":
            self.player_hand = []
            self.dealer_hand = []
            self.bet = 0
            self.message = ""
            self.state = "BETTING"
            
            if self.players[self.current_player_name]['money'] <= 0:
                 self.players[self.current_player_name]['money'] = 10
                 self.message = "破產補助 $10"
                 
            self.init_buttons()

        elif code == "QUIT":
            pygame.quit()
            sys.exit()

    def game_over(self, winner=None, player_blackjack=False):
        self.state = "RESULT"
        self.init_buttons()
        
        data = self.players[self.current_player_name]
        data['total'] += 1
        
        if player_blackjack:
            data['wins'] += 1
            data['money'] += int(self.bet * 1.5)
            self.message = "Blackjack! 贏得 1.5倍!"
        elif winner == "Player":
            data['wins'] += 1
            data['money'] += self.bet
            self.message = "恭喜獲勝!"
        elif winner == "Dealer":
            data['money'] -= self.bet
            self.message = "莊家獲勝!"
        else:
            self.message = "平手!"
            
        save_player_data(self.players)

if __name__ == "__main__":
    game = BlackjackGame()
    game.run()