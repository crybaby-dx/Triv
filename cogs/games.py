import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Group, command



class confirm_button(discord.ui.View):
    def __init__(self, client, author, opponent):
        super().__init__()
        self.client = client
        self.author = author
        self.opponent = opponent
        self.timeout = 30

    def disable_buttons(self):
        for child in self.children:
            child.disabled = True
    
    async def interaction_check(self, interaction: discord.Interaction[discord.Client]) -> bool:
        return interaction.user == self.opponent

    
    @discord.ui.button(label='Confirm')
    async def confirm_but(self, interaction : discord.Interaction, button: discord.ui.Button):
        self.disable_buttons()
        await interaction.message.edit(view=self)
        self.client.curr_players.append(self.author.id)
        self.client.curr_players.append(self.opponent.id)
        await interaction.channel.send(f'{self.author.mention} is playing Tic-Tac-Toe with {self.opponent.mention}.\n{self.author.mention}\'s turn.', view=TicTacToeView(self.author, self.opponent))

    
    @discord.ui.button(label='Cancel')
    async def cancel_but(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.disable_buttons()
        await interaction.message.edit(view=self)
        await interaction.response.send_message('Cancelled.')


class TicTacToeButton(discord.ui.Button):
    def __init__(self, x, y):
        super().__init__(label='\u200b', style=discord.ButtonStyle.secondary, row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        view: TicTacToeView = self.view
        if self.label != '\u200b' or interaction.user != view.current_player:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return

        self.label = 'X' if view.current_player == view.player1 else 'O'
        self.style = discord.ButtonStyle.success if view.current_player == view.player1 else discord.ButtonStyle.danger
        self.disabled = True

        view.board[self.y][self.x] = self.label
        

        # Track moves
        if view.current_player == view.player1:
            view.player1_moves.append(self)
            if len(view.player1_moves) > 3:
                first_move = view.player1_moves.pop(0)
                first_move.label = '\u200b'
                first_move.style = discord.ButtonStyle.secondary
                first_move.disabled = False
                view.board[first_move.y][first_move.x] = ''
        else:
            view.player2_moves.append(self)
            if len(view.player2_moves) > 3:
                first_move = view.player2_moves.pop(0)
                first_move.label = '\u200b'
                first_move.style = discord.ButtonStyle.secondary
                first_move.disabled = False
                view.board[first_move.y][first_move.x] = ''

        winner = view.check_winner()

        if winner or view.is_full():
            for child in view.children:
                child.disabled = True
            await interaction.response.edit_message(content=f'Game over! Winner: {view.current_player.mention}' if winner else 'Game over! It\'s a tie!', view=view)
            interaction.client.curr_players.remove(view.player1.id)
            interaction.client.curr_players.remove(view.player2.id)
        else:
            view.current_player = view.player2 if view.current_player == view.player1 else view.player1
            if view.current_player == view.player1 and len(view.player1_moves) == 3:
                first_move = view.player1_moves[0]
                first_move.style = discord.ButtonStyle.secondary

            elif view.current_player == view.player2 and len(view.player2_moves) == 3:
                first_move = view.player2_moves[0]
                first_move.style = discord.ButtonStyle.secondary

            await interaction.response.edit_message(content=f'{view.current_player.mention}\'s turn', view=view)

            


class TicTacToeView(discord.ui.View):
    def __init__(self, player1, player2):
        super().__init__()
        self.current_player = player1
        self.player1 = player1
        self.player2 = player2
        self.player1_moves = []
        self.player2_moves = []
        self.board = [['' for _ in range(3)] for _ in range(3)]
        for y in range(3):
            for x in range(3):
                self.add_item(TicTacToeButton(x, y))

    def check_winner(self):
        for row in self.board:
            if row[0] == row[1] == row[2] != '':
                return row[0]
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != '':
                return self.board[0][col]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            return self.board[0][2]
        return None

    def is_full(self):
        return all(self.board[y][x] != '' for x in range(3) for y in range(3))
    
    async def interaction_check(self, interaction: discord.Interaction[discord.Client]) -> bool:
        return interaction.user == self.player1 or interaction.user == self.player2



class games(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.curr_players = []


    play_group = Group(name='play', description='games group')


    @play_group.command(name='ttt', description='tic tac toe')
    @app_commands.checks.has_any_role(750117211087044679, 775950201940606976)
    async def ttt(self, interaction: discord.Interaction, user: discord.Member):
        if interaction.user.id in self.client.curr_players:
            return await interaction.response.send_message(f"You're already in a game!", ephemeral=True)
        if user.id in self.client.curr_players:
            return await interaction.response.send_message(f"They're already in a game!", ephemeral=True)
        await interaction.response.send_message(f"{user.mention}, {interaction.user.mention} is challenging you to a tic-tac-toe game.", view=confirm_button(client=self.client, author=interaction.user, opponent=user))












async def setup(client):
    await client.add_cog(games(client))