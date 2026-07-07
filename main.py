import discord
from discord.ext import commands
import os

# --------------------------------------------------
# 選ぶ式（ドロップダウンメニュー）の動作を定義
# --------------------------------------------------
class RoleDropdown(discord.ui.Select):
    def __init__(self):
        # ⬇️ IDの代わりに、valueに「ロールの名前」をそのまま入れます ⬇️
        options = [
            discord.SelectOption(label="ゲーム好き", description="ゲームをよくする人向け", value="ゲーム好き", emoji="🎮"),
            discord.SelectOption(label="プログラマー", description="コードを書く人向け", value="プログラマー", emoji="💻"),
            discord.SelectOption(label="お知らせ通知", description="通知を受け取りたい人向け", value="お知らせ通知", emoji="🔔")
        ]
        
        super().__init__(
            placeholder="欲しいロールを選んでね！",
            min_values=0, 
            max_values=3, # 選択肢の数に合わせて変更してください
            options=options,
            custom_id="role_select_menu_by_name"
        )

    async def callback(self, interaction: discord.Interaction):
        # パネルで管理しているロールの名前リスト
        panel_role_names = ["ゲーム好き", "プログラマー", "お知らせ通知"]
        
        # ユーザーがメニューから選んだロールの名前リスト
        selected_role_names = self.values
        
        roles_to_add = []
        roles_to_remove = []
        
        # それぞれのロール名について、付与するか外すかをチェック
        for role_name in panel_role_names:
            # サーバーのロール一覧から、名前が一致するものを探す（ID不要！）
            role = discord.utils.get(interaction.guild.roles, name=role_name)
            
            if not role:
                continue # サーバーにその名前のロールが無ければスキップ
                
            if role_name in selected_role_names:
                # 選ばれていて、まだ持っていなければ「付与リスト」へ
                if role not in interaction.user.roles:
                    roles_to_add.append(role)
            else:
                # 選ばれていなくて、すでに持っていれば「剥奪リスト」へ
                if role in interaction.user.roles:
                    roles_to_remove.append(role)
        
        # 実際にまとめてロールを付与・剥奪
        if roles_to_add:
            await interaction.user.add_roles(*roles_to_add)
        if roles_to_remove:
            await interaction.user.remove_roles(*roles_to_remove)
            
        await interaction.response.send_message("ロールの設定を更新したよ！", ephemeral=True)


# --------------------------------------------------
# パネル（メニューを乗せる枠）を定義
# --------------------------------------------------
class RolePanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # ずっと使えるようにする
        self.add_item(RoleDropdown())


# --------------------------------------------------
# Bot本体の設定
# --------------------------------------------------
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # 起動時にViewを登録
        self.add_view(RolePanelView())

    async def on_ready(self):
        print(f"ログイン完了: {self.user}")


bot = MyBot()

# 「!panel」で選ぶ式のロールパネルを表示
@bot.command()
async def panel(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("このコマンドは管理者だけが使えるよ。")
        return
        
    embed = discord.Embed(
        title="ロール選択パネル",
        description="下のメニューから欲しいロールを選んでね！\n複数選んだり、チェックを外して外すこともできるよ。",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=RolePanelView())


# Renderの環境変数からトークンを取得して起動
if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("エラー: DISCORD_TOKENが設定されてないよ。")
    else:
        bot.run(token)
