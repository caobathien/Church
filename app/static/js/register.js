document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    const emailInput = document.querySelector("input[name='email']");

    if (!form || !emailInput) return;

    form.addEventListener("submit", (e) => {
        const email = emailInput.value.trim();
        const emailError = document.querySelector(".email-error");

        // Xóa thông báo cũ nếu có
        if (emailError) emailError.remove();

        // Kiểm tra đuôi @gmail.com
        if (!email.endsWith("@gmail.com")) {
            e.preventDefault(); // Ngăn submit
            showEmailError(emailInput, "Địa chỉ email phải kết thúc bằng @gmail.com");
        }
    });

    // Hiển thị lỗi trực quan
    function showEmailError(input, message) {
        input.classList.add("is-invalid");

        const errorDiv = document.createElement("div");
        errorDiv.classList.add("invalid-feedback", "email-error");
        errorDiv.textContent = message;

        // Nếu chưa có feedback thì thêm vào
        if (!input.parentNode.querySelector(".invalid-feedback")) {
            input.parentNode.appendChild(errorDiv);
        }

        input.focus();

        // Khi người dùng gõ lại, xóa lỗi
        input.addEventListener("input", () => {
            input.classList.remove("is-invalid");
            const err = input.parentNode.querySelector(".email-error");
            if (err) err.remove();
        }, { once: true });
    }
});
