function sendNameForm() {
    names = document.getElementById('correct-name').value
    nameForm = document.getElementById('name-form')

    const url = "http://127.0.0.1:5000/addname";

    var data = new FormData();
    data.set("name", names);

    fetch(url,
        {
            method: "POST",
            body: data
        })
        .then(function (res) {
            console.log(res)
            if (res.status === 201) {
                var toastLiveExample = document.getElementById('liveToast')
                var toast = new bootstrap.Toast(toastLiveExample)
                toast.show()
            }
        })
        .catch(error => console.log(error))

    nameForm.reset()
    return false;
}
