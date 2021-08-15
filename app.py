from flask import Flask, render_template, request, redirect, url_for
from get_info import get_my_info, get_oppo_info, champ_history, rune_info, radar_data, get_champ_name, get_spell_name

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/result')
def search_result():
    nickname = request.args.get('nickname')
    result = get_my_info(nickname)
    #유저 정보가 없는 경우
    if not result:
        return redirect('/')
    #유저가 지금 플레이중이 아닌 경우
    elif not result['now_playing']:
        return render_template('notPlaying.html', result = result)
    #정상적으로 작동하는 경우
    else:
        #내 정보를 넣으면 상대를 매칭하여 상대 정보도 알아냄
        opponent = get_oppo_info(result)
        #상대방 챔피언의 통계 알아내기
        infos = champ_history(opponent)
        rune = rune_info(opponent)

        spell = get_spell_name(rune)

        name1 = get_champ_name(result)
        name2 = get_champ_name(opponent)
        radar = radar_data(infos)

        wr = [infos['wins'], infos['losses']]
        kda = [infos['kills'], infos['deaths'], infos['assists']]

        return render_template(

            'result1.html', 

            result = result, 

            opponent = opponent,

            infos = infos,

            name1 = name1,

            name2 = name2,

            rune = rune,

            spell = spell,

            radar = radar,
            wr = wr,
            kda = kda
            )

if __name__ == '__main__':
    app.run(debug=True)
    #localhost:8080
