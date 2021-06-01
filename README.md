

## How to Run

- Step 1: Make sure you have Python 'python version 3.7'

- Step 2: Install the requirements: `pip install -r requirements.txt`

- Step 3: Go to this app's directory and run `python app.py`



## HTML : index.html 

~~~
    <div id='bodybox'>
    <div id='chatboarder'>
        <p id="chatlog7" class="chatlog">&nbsp;</p>
        <p id="chatlog6" class="chatlog">&nbsp;</p>
        <p id="chatlog5" class="chatlog">&nbsp;</p>
        <p id="chatlog4" class="chatlog">&nbsp;</p>
        <p id="chatlog3" class="chatlog">&nbsp;</p>
        <p id="chatlog2" class="chatlog">&nbsp;</p>
        <p id="chatlog1" class="chatlog">&nbsp;</p>
        <input type="text" name="chat" id="chatbox" value=" ">
    </div>

    <h4>Emotion Check</h4>
    <div id="emotions_">{{result_emotions}} </div>
~~~


## HTML : scirpt
~~~
<script>

$('#chatbox').keydown(function(e){
  if(e.keyCode == 13){
            var id = $('#chatbox').val();
            var postdata = {
                'id':id
            }
            $.ajax({
                type: 'POST',
                // url: '{{url_for("ajax")}}',
                url: '{{url_for("FUN_root")}}',
                //url: '/',
                data: JSON.stringify(postdata),
                dataType : 'JSON',
                contentType: "application/json",
                success: function(data){
                    // alert('result_emotions:' + data.result_emotions + "---->answer:" + data.answer);

                    document.getElementById("emotions_").innerHTML  = '<span style="color:red">'+data.result_emotions +'</span>';
                    newEntry(data.answer);

                },
                error: function(request, status, error){
                    // alert('ajax 통신 실패')
                    // alert(error);
                }
            })
          }
        })


var messages = [], // 대화를 담기 위한 리스트 변수 설정
    lastUserMessage = "", //사용자의 마지막 메시지 변수 선언 - 문자열
    botMessage = "", // 봇의 메시지에 대한 변수 선언 - 역시 문자열
    botName = 'Chatbot' // 쳇봇 이름 선언 - 문자열

//var user_input = {{ user_input }};
//var chatbot_input = {{ chatbot_input }};
var chatbot_input = "nice!!!";

// 쳇봇의 대화를 입력할 수 있다.
function chatbotResponse(answer_data) {

    botMessage = answer_data // {{answer_}}; //기본 메시지................>>>> app.py에서 입력한 답변이 여기로 와서 html 페이지에 표시되어야 함

    if (!botMessage) { 

        // 이하 조건문은 사용자의 입력을 받았을 때 어떤 답변을 해야 하는지에 대한 대화 조건이다.
        if (lastUserMessage === 'hi') {
                botMessage = 'Howdy!';
            }

        if (lastUserMessage === 'How do others perceive you?') {
            botMessage = 'People usually listen to me and respond to me.';
        }

        else if (lastUserMessage === 'name') {
            botMessage = 'My name is ' + botName;
        }

        else if (lastUserMessage === "hello") {
            botMessage = chatbot_input;
        }

    }
   

    // 쳇봇 파이선과 연동하여 여기 값을 파이썬코드로 보내고 다시 결과값을 가져오는 것으로 코드 구현할 것
}

//
// 대화를 입력하고 엔터를 쳤을 때 
// 입출력 경과에 대한 함수임
function newEntry(answer) {
    // 사용자가 입력창(chatbox)에 뭐라도 입력하면 실행한다.
    // 입력창이 비어있지 않다면 
    if (document.getElementById("chatbox").value != "") {
        // chatbox의 값을 가져와서 lastUserMessage에 넣는다.
        lastUserMessage = document.getElementById("chatbox").value;
        // lastUserMessage를 서버로 보내서 감성분석후 다시 index.html 페이지에 뿌린다.

        //그리고 나서, chatbox의 값을 비워버린다. 즉, 빈 문자열을 가져와서 채운다.
        document.getElementById("chatbox").value = "";
        // 대화 리스트에 마지막 문자(위에서 입력한 뭐라도...)열을 담는다.
        messages.push(lastUserMessage);
        // 그리고나서, 답변함수를 실행한다.
        chatbotResponse(answer);
        //쳇봇의 이름과 쳇봇이 생성한 메시지를 메시지리스트에 넣느다.
        messages.push("<b>" + botName + ":</b> " + botMessage)
        // 메시지를 text to speech function written 기능으로 구현한다. 
        Speech(botMessage);
        //8단계의 대화까지만 html 창에 출력한다. 로그에 기록한다.
        for (var i = 1; i < 8; i++) {
            if (messages[messages.length - i])
            // 쳇로그에 저장된 문자열을 가져온다. 그 문자열은 html로 구현한 대화들이다.
                document.getElementById("chatlog" + i).innerHTML = messages[messages.length - i];
        }
    }
}

//text to Speech
//https://developers.google.com/web/updates/2014/01/Web-apps-that-talk-Introduction-to-the-Speech-Synthesis-API
function Speech(say) {
    if ('speechSynthesis' in window) {
        var utterance = new SpeechSynthesisUtterance(say);
        //utterance.volume = 1; // 0 to 1
        //utterance.rate = 1; // 0.1 to 10
        //utterance.pitch = 1; //0 to 2
        //utterance.text = 'Hello World';
        //utterance.lang = 'en-US';
        speechSynthesis.speak(utterance);
    }
}

//runs the keypress() function when a key is pressed
document.onkeypress = keyPress;
//if the key pressed is 'enter' runs the function newEntry()
function keyPress(e) {
    var x = e || window.event;
    var key = (x.keyCode || x.which);
    // 13번이 enter 키다. enter 값이 key에 할당되거나 아니면 다른 어떤 키값이 입력된다면, 즉시 newEntry() 함수 실행
    if (key == 13 || key == 3) {
    
    }
}
</script>
~~~

## app.py

~~~

@app.route('/', methods = ['POST', 'GET'])   
def FUN_root():
    if request.method == 'POST':

        data = request.get_json()
        print("#"*100)
        # 이 데이터를 입력으로 사용해야 함
        print('data: ', data)

        # 여기에 쳇봇 코드를 넣어야 함
        data = data['id']
        print('data: ', data) 

        # 여기서 생성한 answer_ 를 html에 보내야 함
        answer_ = chat_start(data)
        print('ChatBot Answer_:', answer_)

        result_emotions = Sentiments_analysis(str(data))
        # 감성분석 결과는 콘솔에 기록됨
        print('result_emotions :' , result_emotions)
        
        ######### set ->list-> string  변환  
        result_emotions_list= list(result_emotions)
        result_emotions = ",".join(result_emotions_list)

        emotion_check(result_emotions)

        data = {
            "result_emotions" : result_emotions,
            "answer" : answer_
            
        }

        return jsonify(data)

    else: ### GET 방식 
        # result_emotions = "test"
        # answer_ = "test"
        # result_fin =  render_template("index.html",result_emotions = result_emotions, answer_ = answer_)
        result_fin =  render_template("index.html")

    return result_fin


def emotion_check(input_value):
    result = input_value
    return render_template("index.html", result_emotions = result)



@app.route('/ajax', methods=['POST'])
def ajax():
    data = request.get_json()
    # print('data: ', data) # 이 데이터를 입력으로 사용해야 함
    # 여기에 쳇봇 코드를 넣어야 함
    data = data['id']
    print('data: ', data) 
    result_emotions = Sentiments_analysis(str(data))
    print(result_emotions)

    return jsonify(result = "success", result2= result_emotions)


~~~

## Chatbot 

- to training: python train.py --datasetdir=datasets/cornell_movie_dialog

- to run : python chat.py datasets/cornell_movie_dialog/trained_model_v1/best_weights_training.ckpt

## Download movie dialogue corpus

- https://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html



## References

- http://flask.pocoo.org/
- https://www.tutorialspoint.com/flask/

