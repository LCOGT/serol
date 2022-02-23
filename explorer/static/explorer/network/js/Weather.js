import axios from 'axios'

export default{
  getStatus() {
    return axios.get()
      .then(response =>{
        return response.data
      })
  }
}
