// 선택적 UX 개선. 이 파일이 없어도 폼만으로 모든 기능이 동작한다.
(function () {
  // 제목 수정: 포커스를 벗어났는데 내용이 바뀌었으면 자동 저장
  document.querySelectorAll(".todo__title").forEach(function (input) {
    var original = input.value;
    input.addEventListener("blur", function () {
      if (input.value.trim() !== original && input.value.trim() !== "") {
        input.form.submit();
      } else {
        input.value = original;
      }
    });
    input.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { input.value = original; input.blur(); }
    });
  });

  // 추가 입력창에 포커스 유지 (페이지 전환 후에도)
  var addInput = document.querySelector(".add__input");
  if (addInput && !document.activeElement.classList.contains("todo__title")) {
    addInput.focus();
  }
})();
