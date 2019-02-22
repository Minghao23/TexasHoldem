
var game = new Vue({
  delimiters: ['[[', ']]'],
  el: '#texas_game',
  components: {
    
  },
  data() {
    return {
      page: {},
      pos: -1,
      gamePos:[1,2,3,4,5,6,7,8],
      gameInfo:{
        palyers: [],
        status:''
      },
      raiseMoney:0,
      curPlayer:{},
      inTurn: false
    }
  },
  computed: {
    isTurn(){
      return this.gameInfo.active_player_pos == this.pos;
    }
  },
  methods: {
    startGame: function() {
      axios.get(`/api/v0/texas/start/${this.pos}/`)
      .then((resp) => {
        if(resp.data.status == 1) {
          console.log("游戏开始！");
        } else {
          this.$alert('开始异常！');
        }
      })
      .catch((error) => {
        console.log(error);
        this.$alert('游戏开始异常！');
      });
    },

    check: function() {
      axios.get(`/api/v0/texas/check/${this.pos}/`)
      .then((resp) => {
        if(resp.data.status == 1) {
          console.log("check！");
        } else {
          this.$alert('check异常！');
        }
      })
      .catch((error) => {
        console.log(error);
        this.$alert('check异常！');
      });
    },

    call: function() {
      axios.get(`/api/v0/texas/call/${this.pos}/`)
      .then((resp) => {
        if(resp.data.status == 1) {
          console.log("跟注成功！");
        } else {
          this.$alert('跟注异常！');
        }
      })
      .catch((error) => {
        console.log(error);
        this.$alert('跟注异常！');
      });
    },

    fold: function() {
      axios.get(`/api/v0/texas/fold/${this.pos}/`)
      .then((resp) => {
        if(resp.data.status == 1) {
          console.log("弃牌成功！");
        } else {
          this.$alert('弃牌异常！');
        }
      })
      .catch((error) => {
        console.log(error);
        this.$alert('弃牌异常！');
      });
    },

    raise: function() {
      axios.get(`/api/v0/texas/raise/${this.pos}/${this.raiseMoney}/`)
      .then((resp) => {
        if(resp.data.status == 1) {
          console.log("加注成功！");
        } else {
          this.$alert('加注异常！');
        }
      })
      .catch((error) => {
        console.log(error);
        this.$alert('加注异常！');
      });
    },

    heartBeat: function() {
      let that = this;
      let heartbeat = function() {
        axios.get(`/api/v0/texas/heartbeat/${that.pos}/`)
        .then((resp) => {
          let result = resp.data;
          that.gameInfo = result.data;
          that.extractCurPlayer();
          that.supplePos();
          setTimeout(function () {
            heartbeat();
          }, 2000);

          console.log(that.gameInfo);
        }).catch((error) => {
          console.log(error);
          that.$alert('掉线中...');
        });
      }
      heartbeat();
    },

    extractCurPlayer: function(){
      for (let item of this.gameInfo.players) {
        if (item.pos == this.pos) {
          this.curPlayer = item;
          break;
        }
      }
    },

    supplePos: function(){
      if (this.gameInfo.players.length < 8) {
        let addN = 8 - this.gameInfo.players.length;
        for (let i = 0; i < addN; i++) {
          this.gameInfo.players.push({});
        }
      }
    }
  },
  beforeMount(){
    // 将views.py中传递过来的暂存在body的data中，然后取出来进行json解析，存在data.page中，并删除dom中的残留数据。
    this.page = JSON.parse(document.getElementsByTagName('body')[0].getAttribute('data-page') || '{}');
    console.log(this.page);
    this.pos = this.page.position;

    this.heartBeat();
  }
});
