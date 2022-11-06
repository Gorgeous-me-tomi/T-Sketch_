function pagination(page){
    let pagContents = document.getElementsByClassName('pag-contents')
    let togText = document.getElementsByClassName('tog-text')
    console.log(togText)

    for (let index = 0; index < pagContents.length; index++) {
        if (page == index) {
            pagContents[index].style.display='block'
            togText[index].classList.add("active");
        }

        if (page != index) {
            pagContents[index].style.display='none'
            togText[index].classList.remove("active");
        }

    }
}

