// Получаем элементы страницы
let inputSurname = document.getElementById("inputSurname"); // поле для ввода фамилии
let buttonSearch = document.getElementById("buttonSearch"); // кнопка Поиск по Фамилии
let textScan = document.getElementById("textScan"); // текстовое поле Сканируйте код регистрации участника
let buttonRegister = document.getElementById("buttonRegister"); // кнопка Зарегистрировать нового участника
let listParticipants = document.getElementById("listParticipants"); // список с radio-button участников
let buttonPrint = document.getElementById("buttonPrint"); // кнопка Печать Бейджа
let buttonBack = document.getElementById("buttonBack"); // кнопка Назад
let inputName = document.getElementById("inputName"); // поле для ввода имени
let inputOrganization = document.getElementById("inputOrganization"); // поле для ввода организации
let inputPosition = document.getElementById("inputPosition"); // поле для ввода должности
let buttonSubmit = document.getElementById("buttonSubmit"); // кнопка Зарегистрировать

// Функция для скрытия элементов
function hideElements(...elements) {
  for (let element of elements) {
    element.style.display = "none";
  }
}

// Функция для показа элементов
function showElements(...elements) {
  for (let element of elements) {
    element.style.display = "block";
  }
}

// Функция для очистки списка участников
function clearListParticipants() {
  while (listParticipants.firstChild) {
    listParticipants.removeChild(listParticipants.firstChild);
  }
}

// Функция для создания radio-button с участником
function createRadioButton(participant) {
  let label = document.createElement("label");
  let radio = document.createElement("input");
  radio.type = "radio";
  radio.name = "participant";
  radio.value = participant.id;
  label.appendChild(radio);
  label.appendChild(document.createTextNode(`${participant.surname} ${participant.name} ${participant.organization} ${participant.position}`));
  listParticipants.appendChild(label);
}

// Функция для получения выбранного участника
function getSelectedParticipant() {
  let radios = document.getElementsByName("participant");
  for (let radio of radios) {
    if (radio.checked) {
      return radio.value;
    }
  }
  return null;
}

// Функция для сброса полей ввода
function resetInputs() {
  inputSurname.value = "";
  inputName.value = "";
  inputOrganization.value = "";
  inputPosition.value = "";
}

// Обработчик события нажатия на кнопку Поиск по Фамилии
buttonSearch.addEventListener("click", function() {
  let surname = inputSurname.value; // получаем введенную фамилию
  if (surname) { // если фамилия не пустая
    let xhr = new XMLHttpRequest(); // создаем объект для запроса
    xhr.open("GET", "http://192.168.1.5:8000/api/participants?surname=${surname}"); // открываем запрос с параметром фамилии
    xhr.onload = function() { // устанавливаем функцию, которая будет вызвана при получении ответа
      if (xhr.status == 200) { // если статус ответа 200 (успешно)
        let participants = JSON.parse(xhr.responseText); // парсим ответ в json
        if (participants.length > 0) { // если есть хотя бы один участник
          hideElements(inputSurname, buttonSearch, textScan, buttonRegister); // скрываем элементы на странице
          clearListParticipants(); // очищаем список участников
          for (let participant of participants) { // для каждого участника
            createRadioButton(participant); // создаем radio-button с участником
          }
          showElements(listParticipants, buttonPrint, buttonBack); // показываем элементы на странице
        } else { // если нет участников
          alert("Нет участников с такой фамилией"); // выводим аллерт
        }
      } else if (xhr.status == 500) { // если статус ответа 500 (ошибка сервера)
        alert("Повторите поиск"); // выводим аллерт
      }
    };
    xhr.send(); // отправляем запрос
  } else { // если фамилия пустая
    alert("Введите фамилию"); // выводим аллерт
  }
});

// Обработчик события нажатия на кнопку Печать Бейджа
buttonPrint.addEventListener("click", function() {
  let participantId = getSelectedParticipant(); // получаем выбранного участника
  if (participantId) { // если участник выбран
    let xhr = new XMLHttpRequest(); // создаем объект для запроса
    xhr.open("POST", "http://192.168.1.5:8000/print?participantId=${participantId}"); // открываем запрос с параметром идентификатора участника
    xhr.onload = function() { // устанавливаем функцию, которая будет вызвана при получении ответа
      if (xhr.status == 200) { // если статус ответа 200 (успешно)
        alert("Бейдж напечатан"); // выводим аллерт
        hideElements(listParticipants, buttonPrint, buttonBack); // скрываем элементы на странице
        showElements(inputSurname, buttonSearch, textScan, buttonRegister); // показываем элементы на странице
        resetInputs(); // сбрасываем поля ввода
      } else if (xhr.status == 500) { // если статус ответа 500 (ошибка сервера)
        alert("Повторите печать"); // выводим аллерт
      }
    };
    xhr.send(); // отправляем запрос
  } else { // если участник не выбран
    alert("Выберите участника"); // выводим аллерт
  }
});

// Обработчик события нажатия на кнопку Назад
buttonBack.addEventListener("click", function() {
  hideElements(listParticipants, buttonPrint, buttonBack, inputName, inputOrganization, inputPosition, buttonSubmit); // скрываем элементы на странице
  showElements(inputSurname, buttonSearch, textScan, buttonRegister); // показываем элементы на странице
  resetInputs(); // сбрасываем поля ввода
});

// Обработчик события нажатия на кнопку Зарегистрировать нового участника
buttonRegister.addEventListener("click", function() {
  hideElements(inputSurname, buttonSearch, textScan, buttonRegister); // скрываем элементы на странице
  showElements(buttonBack, inputName, inputOrganization, inputPosition, buttonSubmit); // показываем элементы на странице
});

//// Обработчик события нажатия на кнопку Зарегистрировать
//buttonSubmit.addEventListener("click", function() {
//  let name = inputName.value; // получаем введенное имя
//  let surname = inputSurname.value; // получаем введенную фамилию
//  let organization = inputOrganization.value; // получаем введенную организацию
//  let position = inputPosition.value; // получаем введенную должность
//  if (name && surname && organization && position) { // если все поля заполнены
//    let xhr = new XMLHttpRequest(); // создаем объект для запроса
//    xhr.open("POST", "http://192.168.1.5:8000/api/register"); // открываем запрос
//    xhr.setRequestHeader("Content-Type", "application/json"); // устанавливаем заголовок с типом контента
//    xhr.onload = function() { // устанавливаем функцию, которая будет вызвана при получении ответа
//      if (xhr.status == 200) { // если статус ответа 200 (успешно)
//        let participant = JSON.parse(xhr.responseText); // парсим ответ в json
//        hideElements(inputName, inputOrganization, inputPosition, buttonSubmit); // скрываем элементы на странице
//        clearListParticipants(); // очищаем список участников
//        createRadioButton(participant); // создаем radio-button с участником
//        showElements(listParticipants, buttonPrint, buttonBack); // показываем элементы на странице
//      } else if (xhr.status == 500) { // если статус ответа 500 (ошибка сервера)
//        alert("Повторите регистрацию"); // выводим аллерт
//      }
//    };
//    xhr.send(JSON.stringify({name, surname, organization, position}))
//    }
//    }