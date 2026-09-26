(function () {
  const form = document.getElementById("entry-form");
  const equipment = document.getElementById("id_equipment");
  const totalHours = document.getElementById("id_total_hours");
  const previous = document.getElementById("previous-hours");
  const maximum = document.getElementById("maximum-hours");
  const message = document.getElementById("client-message");
  const card = document.getElementById("reading-card");

  if (!form || !equipment) return;

  function latestUrl(id) {
    return form.dataset.latestUrl.replace("/0/", `/${id}/`);
  }

  function setReading(data) {
    if (!data.configured) {
      previous.textContent = "—";
      maximum.textContent = "—";
      card.dataset.configured = "false";
      message.textContent = data.message || "প্রথমে Admin থেকে Initial Hours সেট করুন।";
      return;
    }
    previous.textContent = data.previous;
    maximum.textContent = data.maximum;
    card.dataset.configured = "true";
    message.textContent = "";
  }

  async function updateReading() {
    if (!equipment.value) {
      previous.textContent = "—";
      maximum.textContent = "—";
      card.dataset.configured = "false";
      message.textContent = "";
      return;
    }
    try {
      const response = await fetch(latestUrl(equipment.value), {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      if (!response.ok) throw new Error("Unable to load reading");
      setReading(await response.json());
    } catch (error) {
      message.textContent = "Reading পাওয়া যায়নি। আবার চেষ্টা করুন।";
    }
  }

  equipment.addEventListener("change", updateReading);
  form.addEventListener("submit", function (event) {
    if (card.dataset.configured !== "true") {
      event.preventDefault();
      message.textContent = "প্রথমে Admin থেকে Initial Hours সেট করুন।";
      return;
    }
    if (totalHours.value && totalHours.value === previous.textContent) {
      if (!window.confirm("Previous এবং Current Hours একই। তথ্যটি যাচাই করে সংরক্ষণ করবেন?")) {
        event.preventDefault();
      }
    }
  });
  if (equipment.value) updateReading();
})();