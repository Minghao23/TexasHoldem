var join = new Vue({
  delimiters: ['[[', ']]'],
  el: '#join_game',
  components: {},
  data() {
    return {
      username: ""
    }
  },
  computed: {
  },
  methods: {
    joinGame: function(){
      axios.get('/api/v0/texas/join/' + this.username + '/')
      .then((resp) => {
        let result = resp.data
        let pos = result.pos;
        console.log(resp);
        window.location.href = `/game/?pos=${pos}`;
      })
      .catch((error) => {
        console.log(error);
        this.$alert('加入游戏失败！');
      });
    }
  },
  beforeMount(){
    this.page = JSON.parse(document.getElementsByTagName('body')[0].getAttribute('data-page') || '{}');
  }
});
