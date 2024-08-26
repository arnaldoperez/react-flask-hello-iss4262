import React, { useEffect } from "react"

export default function LoginPaypalButton() {
  useEffect(() => {
    paypal.use(['login'], function (login) {
      login.render({
        "appid": process.env.PAYPAL_CLIENT_ID,
        "authend": "sandbox",
        "containerid": "paypal-button",
        "responseType": "code",
        "locale": "es-es",
        "buttonType": "CWP",
        "buttonShape": "pill",
        "buttonSize": "lg",
        "fullPage": "true",
        "returnurl": "https://curly-succotash-jjvvj79gvxxfqv64-3000.app.github.dev"
      });
    });
  }, [])

  function buildLoginButtonURL() {
    let url = "https://www.sandbox.paypal.com/signin/authorize?flowEntry=static"
    url += `&client_id=${process.env.PAYPAL_CLIENT_ID}`
    url += `&scope=basic`
    url += `&redirect_uri=${process.env.FRONTEND_URL}`
    return url
  }
  return <span > <a href={buildLoginButtonURL()}>Login con paypal</a> </span>
}
