import React, { useState, useEffect, useContext } from "react";
import PropTypes, { func } from "prop-types";
import { Link, useParams } from "react-router-dom";
import { Context } from "../store/appContext";
import rigoImageUrl from "../../img/rigo-baby.jpg";

export const Single = props => {
  const [status, setStatus] = useState("")
  const { store, actions } = useContext(Context);
  const params = useParams();

  async function submitForm(e) {
    e.preventDefault()
    let formdata = new FormData(e.target)
    setStatus("Cargando...")
    await actions.uploadProfilePicture(formdata)
    setStatus("Listo")
  }

  return (
    <div className="jumbotron">
      <h1 className="display-4">Cambio de foto de perfil</h1>
      <h2>{status}</h2>
      <img src={store.profilePicture} />
      <hr className="my-4" />

      <form onSubmit={submitForm}>
        <div class="mb-3">
          <label for="formFile" class="form-label">Ingrese foto de perfil</label>
          <input class="form-control" type="file" id="formFile" name="profilePic" />
          <button type="submit" class="btn btn-primary">Enviar</button>
        </div>
      </form>
    </div>
  );
};

Single.propTypes = {
  match: PropTypes.object
};
