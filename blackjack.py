
import random
import os


# ======== 玩家資料管理函數 ========

def load_player_data(filename="players.txt"):
    # 取得程式所在的資料夾路徑
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    
    players = {}
    
    # 檢查檔案是否存在
    if not os.path.exists(filepath):
        return players
    
    # 讀取檔案
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:  # 忽略空行
                    # 解析資料: alice,100,2,1,50%
                    parts = line.split(',')
                    if len(parts) == 5:
                        name = parts[0]
                        money = int(parts[1])
                        total = int(parts[2])
                        wins = int(parts[3])
                        win_rate = parts[4]
                        
                        players[name] = {
                            'money': money,
                            'total': total,
                            'wins': wins,
                            'win_rate': win_rate
                        }
    except Exception as e:
        print(f"讀取檔案時發生錯誤: {e}")
    
    return players


def save_player_data(players, filename="players.txt"):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            for name, data in players.items():
                # 計算勝率
                if data['total'] > 0:
                    win_rate = (data['wins'] / data['total']) * 100
                    win_rate_str = f"{win_rate:.1f}%"
                else:
                    win_rate_str = "0.0%"
                
                # 寫入格式: 名字,金額,總場數,勝場數,勝率
                line = f"{name},{data['money']},{data['total']},{data['wins']},{win_rate_str}\n"
                file.write(line)
    except Exception as e:
        print(f"寫入檔案時發生錯誤: {e}")


def get_or_create_player(players):
    name = input("請輸入您的姓名: ").strip()
    
    if name in players:
        # 現有玩家
        print(f"\n歡迎回來, {name}!")
        print(f"目前持有金額: ${players[name]['money']}")
        print(f"總比賽場數: {players[name]['total']}")
        print(f"勝場數: {players[name]['wins']}")
        print(f"勝率: {players[name]['win_rate']}")
    else:
        # 新玩家
        print(f"\n歡迎新玩家 {name}!")
        print("系統已為您開設帳戶,起始金額: $100")
        players[name] = {
            'money': 100,
            'total': 0,
            'wins': 0,
            'win_rate': '0.0%'
        }
    
    return name, players[name]


def check_bankruptcy(player_data):
    if player_data['money'] <= 0:
        print("\n" + "=" * 50)
        print("你已賠光所有資產，在此贊助$10")
        print("=" * 50)
        player_data['money'] = 10


def get_bet_amount(player_data):
    while True:
        print(f"\n目前持有金額: ${player_data['money']}")
        try:
            bet = int(input(f"請輸入下注金額 (最少$10, 最多${player_data['money']}): "))
            
            if bet < 10:
                print("下注金額不得低於$10")
            elif bet > player_data['money']:
                print(f"下注金額不得超過您的持有金額 ${player_data['money']}")
            else:
                return bet
        except ValueError:
            print("請輸入有效的數字")


def update_game_result(player_data, bet, is_win):
    # 增加總場數
    player_data['total'] += 1
    
    if is_win == True:
        # 獲勝: 增加下注金額
        player_data['wins'] += 1
        player_data['money'] += bet
        print(f"\n[+] 獲勝! 贏得 ${bet}, 目前持有: ${player_data['money']}")
    elif is_win == False:
        # 失敗: 扣除下注金額
        player_data['money'] -= bet
        print(f"\n[-] 失敗! 損失 ${bet}, 目前持有: ${player_data['money']}")
    else:
        # 平手: 不改變金額
        print(f"\n[=] 平手! 金額不變, 目前持有: ${player_data['money']}")
    
    # 計算勝率
    if player_data['total'] > 0:
        win_rate = (player_data['wins'] / player_data['total']) * 100
        player_data['win_rate'] = f"{win_rate:.1f}%"


# ======== 卡牌相關函數 ========

def create_deck():
    """
    建立一副52張的撲克牌
    
    回傳:
        牌組列表,每張牌是 (花色, 點數) 的元組
    
    功能說明:
        - 建立4種花色 (黑桃、紅心、方塊、梅花)
        - 每種花色13張牌 (A, 2-10, J, Q, K)
        - 總共52張牌
    """
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    deck = []
    
    for suit in suits:
        for rank in ranks:
            deck.append((suit, rank))
    
    return deck


def shuffle_deck(deck):
    """
    洗牌
    
    參數:
        deck: 牌組列表
    
    回傳:
        洗好的牌組
    
    功能說明:
        - 使用 random.shuffle 隨機打亂牌組順序
        - 確保每局遊戲的牌序都不同
    """
    random.shuffle(deck)
    return deck


def deal_card(deck):
    """
    從牌組發一張牌
    
    參數:
        deck: 牌組列表
    
    回傳:
        發出的牌 (花色, 點數) 或 None (如果牌組已空)
    
    功能說明:
        - 從牌組最後取出一張牌
        - 該牌會從牌組中移除
        - 如果牌組為空,回傳 None
    """
    if len(deck) > 0:
        return deck.pop()
    return None


def card_to_string(card):
    """
    將卡牌轉換成字串
    
    參數:
        card: (花色, 點數) 元組
    
    回傳:
        字串表示,例如 "紅心A" 或 "黑桃K"
    
    功能說明:
        - 將卡牌元組轉換為易讀的字串格式
        - 方便顯示給玩家看
    """
    suit, rank = card
    return f"{suit}{rank}"


def get_card_value(card):
    """
    取得卡牌的點數
    
    參數:
        card: (花色, 點數) 元組
    
    回傳:
        點數值 (整數)
    
    功能說明:
        - J, Q, K: 10點
        - A: 11點 (預設值,之後會在 adjust_for_ace 中調整)
        - 數字牌: 面值
    """
    suit, rank = card
    
    if rank in ['J', 'Q', 'K']:
        return 10
    elif rank == 'A':
        return 11  # A預設為11,稍後會調整
    else:
        return int(rank)


# ======== 手牌相關函數 ========

def create_hand():
    """
    建立空手牌
    
    回傳:
        手牌字典 {'cards': [], 'value': 0, 'aces': 0}
    
    功能說明:
        - cards: 儲存手牌中的所有卡牌
        - value: 手牌總點數
        - aces: 記錄有幾張A (用於調整點數)
    """
    return {
        'cards': [],      # 卡牌列表
        'value': 0,       # 總點數
        'aces': 0         # A的數量
    }


def add_card_to_hand(hand, card):
    """
    將卡牌加入手牌
    
    參數:
        hand: 手牌字典
        card: 要加入的卡牌
    
    功能說明:
        - 將新卡牌加入手牌列表
        - 增加總點數
        - 如果是A,記錄A的數量
    """
    hand['cards'].append(card)
    hand['value'] += get_card_value(card)
    
    # 如果是A,記錄下來
    suit, rank = card
    if rank == 'A':
        hand['aces'] += 1


def adjust_for_ace(hand):
    """
    調整A的點數
    
    參數:
        hand: 手牌字典
    
    功能說明:
        - 如果總點數超過21且手中有A
        - 將A從11點改成1點 (減去10點)
        - 重複此過程直到點數<=21或沒有A可調整
        - 這是Blackjack的核心規則之一
    """
    while hand['value'] > 21 and hand['aces'] > 0:
        hand['value'] -= 10  # 將一個A從11點變成1點
        hand['aces'] -= 1


def get_hand_value(hand):
    """
    取得手牌的總點數
    
    參數:
        hand: 手牌字典
    
    回傳:
        調整後的總點數
    
    功能說明:
        - 先調整A的點數
        - 回傳最終點數
    """
    adjust_for_ace(hand)
    return hand['value']


def hand_to_string(hand):
    """
    將手牌轉換成字串顯示
    
    參數:
        hand: 手牌字典
    
    回傳:
        字串,例如 "紅心A, 黑桃K (點數: 21)"
    
    功能說明:
        - 列出所有卡牌
        - 顯示總點數
        - 方便顯示給玩家看
    """
    cards_str = ', '.join([card_to_string(card) for card in hand['cards']])
    value = get_hand_value(hand)
    return f"{cards_str} (點數: {value})"


# ======== 遊戲顯示函數 ========

def show_welcome():
    """
    顯示歡迎訊息
    
    功能說明:
        - 顯示遊戲標題
        - 用分隔線美化輸出
    """
    print("=" * 50)
    print("歡迎來到 Blackjack (21點) 遊戲!")
    print("=" * 50)


def show_hands(player_hand, dealer_hand, hide_dealer=False):
    """
    顯示玩家和莊家的手牌
    
    參數:
        player_hand: 玩家手牌字典
        dealer_hand: 莊家手牌字典
        hide_dealer: 是否隱藏莊家的第二張牌
    
    功能說明:
        - 顯示玩家的完整手牌和點數
        - 如果 hide_dealer=True,只顯示莊家第一張牌
        - 如果 hide_dealer=False,顯示莊家完整手牌
        - 遊戲進行中隱藏莊家牌,結束後顯示
    """
    print("\n" + "-" * 50)
    print(f"[玩家] 你的手牌: {hand_to_string(player_hand)}")
    
    if hide_dealer:
        # 只顯示莊家的第一張牌
        first_card = dealer_hand['cards'][0]
        print(f"[莊家] 莊家的手牌: {card_to_string(first_card)}, [隱藏]")
    else:
        print(f"[莊家] 莊家的手牌: {hand_to_string(dealer_hand)}")
    print("-" * 50)


def show_final_result(player_hand, dealer_hand):
    player_value = get_hand_value(player_hand)
    dealer_value = get_hand_value(dealer_hand)
    
    print("\n" + "=" * 50)
    print("最終結果:")
    print(f"[玩家] 你的點數: {player_value}")
    print(f"[莊家] 莊家點數: {dealer_value}")
    print("=" * 50)
    
    if player_value > dealer_value:
        print("\n恭喜你贏了!")
        return True
    elif player_value < dealer_value:
        print("\n很遺憾,你輸了!")
        return False
    else:
        print("\n平手!")
        return None


# ======== 遊戲流程函數 ========

def initial_deal(deck, player_hand, dealer_hand):
    """
    發初始兩張牌給玩家和莊家
    
    參數:
        deck: 牌組
        player_hand: 玩家手牌
        dealer_hand: 莊家手牌
    
    功能說明:
        - 按照Blackjack規則,遊戲開始時各發兩張牌
        - 先給玩家發一張,再給莊家發一張,重複一次
    """
    print("\n發牌中...")
    
    # 發兩張牌給玩家
    add_card_to_hand(player_hand, deal_card(deck))
    add_card_to_hand(player_hand, deal_card(deck))
    
    # 發兩張牌給莊家
    add_card_to_hand(dealer_hand, deal_card(deck))
    add_card_to_hand(dealer_hand, deal_card(deck))


def player_turn(deck, player_hand, dealer_hand):
    """
    玩家的回合
    
    參數:
        deck: 牌組
        player_hand: 玩家手牌
        dealer_hand: 莊家手牌
    
    回傳:
        True (玩家停牌), False (玩家爆牌)
    
    功能說明:
        - 讓玩家選擇要牌(H)或停牌(S)
        - 要牌: 從牌組抽一張牌加入手牌
        - 檢查是否超過21點 (爆牌)
        - 如果爆牌,玩家直接輸掉
        - 停牌: 結束玩家回合
    """
    while True:
        choice = input("\n你要 [H]要牌(Hit) 還是 [S]停牌(Stand)? ").upper()
        
        if choice == 'H':
            # 要牌
            new_card = deal_card(deck)
            print(f"\n你抽到: {card_to_string(new_card)}")
            add_card_to_hand(player_hand, new_card)
            
            print(f"[玩家] 你的手牌: {hand_to_string(player_hand)}")
            
            # 檢查是否爆牌
            if get_hand_value(player_hand) > 21:
                print("\n爆牌了!你輸了!")
                return False
                
        elif choice == 'S':
            # 停牌
            print("\n你選擇停牌")
            return True
        else:
            print("無效的輸入,請輸入 H 或 S")


def dealer_turn(deck, dealer_hand):
    """
    莊家的回合
    
    參數:
        deck: 牌組
        dealer_hand: 莊家手牌
    
    回傳:
        True (莊家停牌), False (莊家爆牌)
    
    功能說明:
        - 莊家按照固定規則行動
        - 點數 < 17: 必須要牌
        - 點數 >= 17: 必須停牌
        - 如果莊家爆牌,玩家獲勝
    """
    print("\n莊家的回合...")
    
    # 莊家必須在點數小於17時要牌
    while get_hand_value(dealer_hand) < 17:
        print("\n莊家點數小於17,必須要牌...")
        new_card = deal_card(deck)
        print(f"莊家抽到: {card_to_string(new_card)}")
        add_card_to_hand(dealer_hand, new_card)
        print(f"[莊家] 莊家的手牌: {hand_to_string(dealer_hand)}")
    
    # 檢查莊家是否爆牌
    if get_hand_value(dealer_hand) > 21:
        print("\n莊家爆牌了!你贏了!")
        return False
    
    return True


def play_game(player_name, player_data):
    # 檢查是否破產
    check_bankruptcy(player_data)
    
    # 顯示歡迎訊息
    show_welcome()
    
    # 下注
    bet = get_bet_amount(player_data)
    print(f"\n本局下注: ${bet}")
    
    # 建立並洗牌
    deck = create_deck()
    shuffle_deck(deck)
    
    # 建立玩家和莊家的手牌
    player_hand = create_hand()
    dealer_hand = create_hand()
    
    # 發初始牌
    initial_deal(deck, player_hand, dealer_hand)
    
    # 顯示初始牌面
    show_hands(player_hand, dealer_hand, hide_dealer=True)
    
    # 檢查是否有人直接拿到 Blackjack (21點)
    if get_hand_value(player_hand) == 21:
        print("\n恭喜!你拿到 Blackjack!")
        show_hands(player_hand, dealer_hand, hide_dealer=False)
        update_game_result(player_data, bet, True)
        return
    
    # 玩家回合
    player_continue = player_turn(deck, player_hand, dealer_hand)
    
    # 如果玩家爆牌,直接輸掉
    if not player_continue:
        update_game_result(player_data, bet, False)
        return
    
    # 顯示莊家的完整手牌
    show_hands(player_hand, dealer_hand, hide_dealer=False)
    
    # 莊家回合
    dealer_continue = dealer_turn(deck, dealer_hand)
    
    # 如果莊家爆牌,玩家獲勝
    if not dealer_continue:
        update_game_result(player_data, bet, True)
        return
    
    # 如果莊家也沒爆牌,判定勝負
    result = show_final_result(player_hand, dealer_hand)
    update_game_result(player_data, bet, result)


# ======== 主程式 ========

def main():
    # 載入玩家資料
    players = load_player_data()
    
    # 取得或建立玩家
    player_name, player_data = get_or_create_player(players)
    
    # 遊戲循環
    while True:
        # 開始新遊戲
        play_game(player_name, player_data)
        
        # 存檔 (每局結束後都要存檔)
        save_player_data(players)
        print("\n[系統] 資料已儲存")
        
        # 重新載入資料 (確保是最新的)
        players = load_player_data()
        print(f"players->{players}")
        player_data = players[player_name]
        
        # 詢問是否再玩一局
        print("\n" + "=" * 50)
        play_again = input("要再玩一局嗎? [Y/N]: ").upper()
        if play_again != 'Y':
            # 顯示最終戰績
            print("\n" + "=" * 50)
            print("最終戰績:")
            print(f"姓名: {player_name}")
            print(f"持有金額: ${player_data['money']}")
            print(f"總比賽場數: {player_data['total']}")
            print(f"勝場數: {player_data['wins']}")
            print(f"勝率: {player_data['win_rate']}")
            print("=" * 50)
            print("\nbye!")
            break


# 執行遊戲
if __name__ == "__main__":
    main()
