const backendUrl = process.env.BACKEND_URL
const getState = ({ getStore, getActions, setStore }) => {
  return {
    store: {
      message: null,
      demo: [
        {
          title: "FIRST",
          background: "white",
          initial: "white"
        },
        {
          title: "SECOND",
          background: "white",
          initial: "white"
        }
      ]
    },
    actions: {
      // Use getActions to call a function within a fuction
      exampleFunction: () => {
        getActions().changeColor(0, "green");
      },

      getMessage: async () => {
        try {
          // fetching data from the backend
          const resp = await fetch(process.env.BACKEND_URL + "/api/hello")
          const data = await resp.json()
          setStore({ message: data.message })
          // don't forget to return something, that is how the async resolves
          return data;
        } catch (error) {
          console.log("Error loading message from backend", error)
        }
      },
      changeColor: (index, color) => {
        //get the store
        const store = getStore();

        //we have to loop the entire demo array to look for the respective index
        //and change its color
        const demo = store.demo.map((elm, i) => {
          if (i === index) elm.background = color;
          return elm;
        });

        //reset the global store
        setStore({ demo: demo });
      },
      changePassword: async (newPassword, token) => {
        const resp = await fetch(backendUrl + "/changepassword", {
          method: "PATCH",
          headers: {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
          },
          body: JSON.stringify({ "new_password": newPassword })
        })
        if (!resp.ok) {
          console.error(resp.statusText)
          return false
        }
        return true
      },
      login: async (email, password) => {
        const resp = await fetch(backendUrl + "/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
          },
          body: JSON.stringify({ email, password })
        })
        if (!resp.ok) {
          console.error(resp.statusText)
          return false
        }
        let { token } = await resp.json()
        setStore({ token })
        localStorage.setItem("token", token)
        return true
      },
      loadSession: () => {
        let token = localStorage.getItem("token")
        setStore({ token })
        let { getProfilePic } = getActions()
        getProfilePic()
      },
      uploadPicture: async (formData) => {
        let { token } = getStore()
        const resp = await fetch(backendUrl + "/profilepic", {
          method: "PATCH",
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Authorization": "Bearer " + token
          },
          body: formData
        })
        if (!resp.ok) {
          console.error(resp.statusText)
          return false
        }
        let { getProfilePic } = getActions()
        getProfilePic()
        return true
      },
      getProfilePic: async () => {
        let { token } = getStore()
        const resp = await fetch(backendUrl + "/profilepic", {
          method: "GET",
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Authorization": "Bearer " + token
          },
        })
        if (!resp.ok) {
          console.error(resp.statusText)
          return false
        }
        let { url } = await resp.json()
        setStore({ profilePicture: url })
      }
    }
  };
};

export default getState;
