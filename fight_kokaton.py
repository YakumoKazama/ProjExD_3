import os
import math
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5 # 爆弾の個数
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy
        self.dire = (+5, 0) #デフォルト右向き

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
            self.dire = (sum_mv[0], sum_mv[1])
        screen.blit(self.img, self.rct)


class Beam:
    """
    こうかとんが放つビームに関するクラス
    """
    def __init__(self, bird: Bird):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん（Birdインスタンス）
        """
        #ビームの向きをこうかとんに合わせる
        self.vx, self.vy = bird.dire[0], bird.dire[1]
        self.angle = math.atan2(-1 * self.vy, self.vx)
        self.angle = math.degrees(self.angle)

        self.img = pg.transform.rotozoom(pg.image.load("fig/beam.png"), self.angle, 1)
        self.rct = self.img.get_rect()
        # self.rct.left = bird.rct.right
        self.rct.centerx = bird.rct.centerx + bird.rct.width * self.vx // 5
        self.rct.centery = bird.rct.centery + bird.rct.height * self.vy // 5
    
    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        if check_bound(self.rct) == (True, True):
            self.rct.move_ip(self.vx, self.vy)
            screen.blit(self.img, self.rct)   


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Score:
    """
    スコアを表示するクラス
    """
    def __init__(self):
        """
        スコアを初期化し、文字列Surfaceを生成する
        """
        self.score = 0
        #Surface生成
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.img = self.fonto.render("スコア:" + str(self.score), 0, (0, 0, 255))
        self.rct = self.img.get_rect()
        #画面左下に表示する
        self.rct.centerx = 100
        self.rct.centery = HEIGHT - 50
    
    def update(self, screen: pg.Surface):
        """
        画面に出力(blit)する
        """
        self.img = self.fonto.render("スコア:" + str(self.score), 0, (0, 0, 255))
        screen.blit(self.img, self.rct)
        

class Explosion:
    """
    爆発エフェクトのクラス
    """
    def __init__(self, bomb: Bomb):
        """
        爆発エフェクトSurfaceを生成
        """
        self.life = 50
        #Surface生成
        self.img = pg.image.load("fig/explosion.gif")
        self.rct = self.img.get_rect()
        self.rct.center = bomb.rct.center
        self.imgs = [self.img, pg.transform.flip(self.img, True, True)]
    
    def update(self, screen: pg.Surface):
        """
        画面に出力(blit)する
        """
        if self.life > 0:
            self.life -= 1
            screen.blit(self.imgs[0], self.rct)


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    bombs = [Bomb((255, 0, 0), 10) for i in range(NUM_OF_BOMBS)] #爆弾インスタンスの配列
    beams = []
    explosions = []
    score = Score()
    clock = pg.time.Clock()
    tmr = 0
    expl_cnt = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                # スペースキー押下でBeamクラスのインスタンス生成
                beams.append(Beam(bird))
        screen.blit(bg_img, [0, 0])
        
        for i, bomb in enumerate(bombs):
            if bird.rct.colliderect(bomb.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("Game Over", True, (255, 0, 0))
                screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
                pg.display.update()
                time.sleep(1)
                return

            for j, beam in enumerate(beams):
                if bomb.rct.colliderect(beam.rct):
                    # 爆弾とビームの衝突時，どちらも消滅する
                    bombs[i], beams[j] = None, None
                    score.score += 1 #得点を足す
                    bird.change_img(6, screen)

                    #Explosion
                    explosions.append(Explosion(bomb))

                    pg.display.update()
            
             #ビーム配列を更新. 画面外のビームも除外する.
            beams = [beam for beam in beams if beam is not None]
            beams = [beam for beam in beams if check_bound(beam.rct) == (True, True)]
        
        bombs = [bomb for bomb in bombs if bomb is not None] #爆弾配列を更新
        explosions = [expl for expl in explosions if expl.life > 0]

        for expl in explosions:
            expl_cnt += 1
            if expl_cnt < 10:
                expl.update(screen)
            else:
                #画像の切り替え
                expl.imgs[0], expl.imgs[1] = expl.imgs[1], expl.imgs[0]
                expl_cnt = 0

        #インスタンス更新
        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        for beam in beams: beam.update(screen)
        for bomb in bombs: bomb.update(screen)
        score.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
