// Получаем элементы страницы
let input = document.getElementById("input"); // поле для ввода фамилии
let searchButton = document.getElementById("searchButton"); // кнопка Поиск по Фамилии
let scanText = document.getElementById("scanText"); // текстовое поле Сканируйте код регистрации участника
let registerButton = document.getElementById("registerButton"); // кнопка Зарегистрировать нового участника
let list = document.getElementById("list"); // список с radio-button для выбора участника
let printButton = document.getElementById("printButton"); // кнопка Печать Бейджа
let backButton = document.getElementById("backButton"); // кнопка Назад
let form = document.getElementById("form"); // форма для регистрации нового участника
let submitButton = document.getElementById("submitButton"); // кнопка Зарегистрировать

// Функция для скрытия элементов
function hide(...elements) {
  for (let element of elements) {
    element.style.display = "none";
  }
}

// Функция для показа элементов
function show(...elements) {
  for (let element of elements) {
    element.style.display = "block";
  }
}

// Функция для очистки списка
function clearList() {
  while (list.firstChild) {
    list.removeChild(list.firstChild);
  }
}

// Функция для создания элемента списка с radio-button
function createListItem(participant) {
  let item = document.createElement("li");
  let radio = document.createElement("input");
  radio.type = "radio";
  radio.name = "participant";
  radio.value = participant.id;
  let label = document.createElement("label");
  label.textContent = `${participant.surname} ${participant.name} (${participant.organization}, ${participant.position})`;
  item.appendChild(radio);
  item.appendChild(label);
  return item;
}

// Функция для обработки ответа от сервера при поиске по фамилии
function handleSearchResponse(response) {
  if (response.status === 200) {
    // Если ответ успешный, парсим json
    response.json().then((data) => {
      // Скрываем текущие элементы
      hide(input, searchButton, scanText, registerButton);
      // Очищаем список
      clearList();
      // Добавляем элементы списка для каждого участника
      for (let participant of data) {
        let item = createListItem(participant);
        list.appendChild(item);
      }
      // Показываем список, кнопку Печать Бейджа и кнопку Назад
      show(list, printButton, backButton);
    });
  } else if (response.status === 500) {
    // Если ответ с ошибкой, выводим аллерт
    alert("Повторите поиск");
  }
}

// Функция для обработки ответа от сервера при печати бейджа
function handlePrintResponse(response) {
  if (response.status === 200) {
    // Если ответ успешный, выводим аллерт
    alert("Бейдж Напечатан");
    // Возвращаемся на начальное состояние страницы
    hide(list, printButton, backButton);
    show(input, searchButton, scanText, registerButton);
  } else if (response.status === 500) {
    // Если ответ с ошибкой, можно повторно нажать кнопку Печать Бейджа
  }
}

// Функция для обработки ответа от сервера при регистрации нового участника
function handleRegisterResponse(response) {
  if (response.status === 200) {
    // Если ответ успешный, парсим json
    response.json().then((data) => {
      // Скрываем текущие элементы
      hide(form, submitButton, backButton);
      // Очищаем список
      clearList();
      // Добавляем элемент списка для нового участника
      let item = createListItem(data);
      list.appendChild(item);
      // Показываем список, кнопку Печать Бейджа и кнопку Назад
      show(list, printButton, backButton);
    });
  } else if (response.status === 500) {
    // Если ответ с ошибкой, можно повторно нажать кнопку Зарегистрировать
  }
}

// Добавляем обработчик события клика на кнопку Поиск по Фамилии
searchButton.addEventListener("click", () => {
  // Получаем введенную фамилию
  let surname = input.value;
  // Отправляем запрос к серверу с фамилией
  fetch(`/search?surname=${surname}`).then(handleSearchResponse);
});

// Добавляем обработчик события клика на кнопку Печать Бейджа
printButton.addEventListener("click", () => {
  // Получаем выбранный radio-button
  let selected = document.querySelector("input[name=participant]:checked");
  if (selected) {
    // Получаем идентификатор выбранного участника
    let id = selected.value;
    // Отправляем запрос к серверу с идентификатором
    fetch(`/print?id=${id}`).then(handlePrintResponse);
  }
});

// Добавляем обработчик события клика на кнопку Назад
backButton.addEventListener("click", () => {
  // Возвращаемся на начальное состояние страницы
  hide(list, printButton, backButton, form, submitButton);
  show(input, searchButton, scanText, registerButton);
});

// Добавляем обработчик события клика на кнопку Зарегистрировать нового участника
registerButton.addEventListener("click", () => {
  // Скрываем текущие элементы
  hide(input, searchButton, scanText, registerButton);
  // Показываем форму, кнопку Зарегистрировать и кнопку Назад
  show(form, submitButton, backButton);
});

// Добавляем обработчик события клика на кнопку Зарегистрировать
submitButton.addEventListener("click", () => {
  // Получаем данные полей ввода
  let surname = form.elements["surname"].value;
  let name = form.elements["name"].value;
  let organization = form.elements["organization"].value;
  let position = form.elements["position"].value;
  // Отправляем запрос к серверу с данными
  fetch(`/register?surname=${surname}&name=${name}&organization=${organization}&position=${position}`).then(
    handleRegisterResponse
  );
});
