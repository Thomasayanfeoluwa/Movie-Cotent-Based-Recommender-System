$.ajaxSetup({
  beforeSend: function (xhr, settings) {
    if (settings.type && settings.type.toUpperCase() === "POST") {
      const token = document.querySelector('meta[name="csrf-token"]').content;
      xhr.setRequestHeader("X-CSRFToken", token);
    }
  },
});

$(document).on("click", ".movie-feedback-button", function () {
  const button = $(this);
  const feedbackSection = button.closest(".movie-feedback");
  const buttons = feedbackSection.find(".movie-feedback-button");
  const status = feedbackSection.find(".movie-feedback-status");

  buttons.prop("disabled", true);
  status.text("Saving your preference...");

  $.ajax({
    type: "POST",
    url: "/api/movie-feedback",
    data: {
      tmdb_movie_id: feedbackSection.find("#tmdb-movie-id").val(),
      preference: button.data("preference"),
    },
    success: function (response) {
      buttons.each(function () {
        const selected = Number($(this).data("preference")) === response.preference;
        $(this)
          .toggleClass("active", selected)
          .attr("aria-pressed", String(selected));
      });
      status.text(
        "Saved. Your preference will shape future recommendations.",
      );
    },
    error: function (xhr) {
      const message =
        xhr.responseJSON?.error || "Could not save your preference. Try again.";
      status.text(message);
    },
    complete: function () {
      buttons.prop("disabled", false);
    },
  });
});

$(document).on("click", ".play-trailer-button, .poster-trailer-trigger", function () {
  const key = $(this).data("trailer-key");
  const video = $("#trailer-video");

  $("#trailer-loader").show();
  video.off("load").hide().on("load", function () {
    $("#trailer-loader").fadeOut();
    video.fadeIn();
  });
  video.attr(
    "src",
    "https://www.youtube.com/embed/" + encodeURIComponent(key) + "?autoplay=1&rel=0",
  );
});

$(document).on("hidden.bs.modal", "#trailerModal", function () {
  $("#trailer-video").attr("src", "");
});

// Loader control functions
function showLoader() {
  $("#loader").css("display", "flex");
}

function hideLoader() {
  $("#loader").css("display", "none");
}

$(function () {
  console.log("Recommender.js loaded");

  // Enable/disable button based on input
  const input = document.getElementById("autoComplete");
  const button = document.querySelector(".movie-button");

  input.addEventListener("input", () => {
    button.disabled = input.value.trim() === "";
  });

  // ENTER key triggers search
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      if (!button.disabled) {
        button.click();
      }
    }
  });

  // Enable/disable button based on input
  const source = document.getElementById("autoComplete");
  source.addEventListener("input", function (e) {
    $(".movie-button").attr("disabled", e.target.value == "");
  });

  const autoCompleteJS = new autoComplete({
    selector: "#autoComplete",
    placeHolder: "Enter the Movie Name",
    data: { src: films, cache: true },
    resultsList: {
      element: (list, data) => {},
      noResults: false,
      maxResults: 5,
    },
    resultItem: { highlight: true },
    events: {
      input: {
        selection: (event) =>
          (autoCompleteJS.input.value = event.detail.selection.value),
      },
    },
  });

  $(".movie-button").on("click", function () {
    console.log("Search button clicked");

    var title = $(".movie").val();
    console.log("Searching for title: " + title);

    if (title === "") {
      $("#recommendation-results").hide();
      $(".fail").show();
    } else {
      showLoader(); // ← SHOW LOADER
      load_details(title);
    }
  });
});

// will be invoked when clicking on the recommended movies
function recommendcard(e) {
  var title = e.getAttribute("title");
  showLoader(); // ← SHOW LOADER
  load_details(title);
}

// get the basic details of the movie from the API (via backend proxy)
function load_details(title) {
  $("#homepage-recommendations").hide();
  $(".fail").hide();

  console.log("Calling TMDB API for movie details: " + title);
  $.ajax({
    type: "GET",
    url: "/api/tmdb/search?query=" + encodeURIComponent(title),

    success: function (movie) {
      console.log("TMDB API Response received");
      if (movie.results.length < 1) {
        console.log("No movies found for title: " + title);
        // Don't show fail message for API results
        // Just hide loader and do nothing
        hideLoader(); // ← HIDE LOADER
      } else {
        console.log("Movie found with ID: " + movie.results[0].id);
        $(".fail").css("display", "none");
        $("#recommendation-results").css("display", "block");
        var movie_id = movie.results[0].id;
        var movie_title = movie.results[0].original_title;
        movie_recs(movie_title, movie_id);
      }
    },
    error: function (xhr, status, error) {
      console.error("TMDB API Error: " + error);
      const apiError = xhr.responseJSON?.error;
      const message = apiError === "TMDB_API_KEY is not configured"
        ? "Movie search needs a TMDB API key. Add TMDB_API_KEY to your .env file, restart the app, and try again."
        : apiError || "Movie search is temporarily unavailable. Check your TMDB API configuration or try again shortly.";
      $(".fail h3").text(message);
      $(".fail").show();
      $("#recommendation-results").hide();
      hideLoader(); // ← HIDE LOADER
    },
  });
}

// passing the movie name to get the similar movies from python's flask
function movie_recs(movie_title, movie_id) {
  console.log("Requesting recommendations from backend for: " + movie_title);
  $.ajax({
    type: "POST",
    url: "/similarity",
    data: { name: movie_title },
    success: function (recs) {
      console.log(
        "Backend response received: " + recs.substring(0, 50) + "...",
      );
      if (
        recs ==
        "Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies"
      ) {
        console.log("Backend reported movie not in database");
        // REMOVED: Don't show fail message
        // Just hide loader and do nothing
        hideLoader(); // ← HIDE LOADER
      } else {
        console.log("Recommendations received, processing metadata...");
        $(".fail").css("display", "none");
        $("#recommendation-results").css("display", "block");
        var movie_arr = recs.split("---");
        var arr = [];
        for (const movie in movie_arr) {
          arr.push(movie_arr[movie]);
        }
        console.log("Recommendations list: " + arr);
        get_movie_details(movie_id, arr, movie_title);
      }
    },
    error: function (xhr, status, error) {
      console.error("Backend recommendation request failed", {
        status: xhr.status,
        error: error,
        response: xhr.responseText,
      });
      const message =
        xhr.responseJSON?.error ||
        `Recommendation request failed (${xhr.status}). Please try again.`;
      $(".fail h3").text(message);
      $(".fail").show();
      hideLoader(); // ← HIDE LOADER
    },
  });
}

// get all the details of the movie using the movie id (via backend proxy)
function get_movie_details(movie_id, arr, movie_title) {
  $.ajax({
    type: "GET",
    url: "/api/tmdb/movie/" + movie_id,
    success: function (movie_details) {
      show_details(movie_details, arr, movie_title, movie_id);
    },
    error: function () {
      alert("API Error!");
      hideLoader(); // ← HIDE LOADER
    },
  });
}

// passing all the details to python's flask for displaying
function show_details(movie_details, arr, movie_title, movie_id) {
  var imdb_id = movie_details.imdb_id;
  var poster =
    "https://image.tmdb.org/t/p/original" + movie_details.poster_path;
  var overview = movie_details.overview;
  var genres = movie_details.genres;
  var rating = movie_details.vote_average;
  var vote_count = movie_details.vote_count;
  var release_date = new Date(movie_details.release_date);
  var runtime = parseInt(movie_details.runtime);
  var status = movie_details.status;
  var genre_list = [];
  for (var genre in genres) {
    genre_list.push(genres[genre].name);
  }
  var my_genre = genre_list.join(", ");
  if (runtime % 60 == 0) {
    runtime = Math.floor(runtime / 60) + " hour(s)";
  } else {
    runtime =
      Math.floor(runtime / 60) + " hour(s) " + (runtime % 60) + " min(s)";
  }
  arr_poster = get_movie_posters(arr);

  movie_cast = get_movie_cast(movie_id);

  ind_cast = get_individual_cast(movie_cast);

  details = {
    title: movie_title,
    tmdb_movie_id: movie_id,
    cast_ids: JSON.stringify(movie_cast.cast_ids),
    cast_names: JSON.stringify(movie_cast.cast_names),
    cast_chars: JSON.stringify(movie_cast.cast_chars),
    cast_profiles: JSON.stringify(movie_cast.cast_profiles),
    cast_bdays: JSON.stringify(ind_cast.cast_bdays),
    cast_bios: JSON.stringify(ind_cast.cast_bios),
    cast_places: JSON.stringify(ind_cast.cast_places),
    imdb_id: imdb_id,
    poster: poster,
    genres: my_genre,
    overview: overview,
    rating: rating,
    vote_count: vote_count.toLocaleString(),
    release_date: release_date.toDateString().split(" ").slice(1).join(" "),
    runtime: runtime,
    status: status,
    rec_movies: JSON.stringify(arr),
    rec_posters: JSON.stringify(arr_poster),
  };

  $.ajax({
    type: "POST",
    data: details,
    url: "/recommend",
    dataType: "html",
    complete: function () {
      hideLoader(); // ← HIDE LOADER WHEN COMPLETE
    },
    success: function (response) {
      $("#recommendation-results").html(response);
      $("#autoComplete").val("");
      $(window).scrollTop(0);
    },
  });
}

// get the details of individual cast (via backend proxy)
function get_individual_cast(movie_cast) {
  cast_bdays = [];
  cast_bios = [];
  cast_places = [];

  for (var cast_id in movie_cast.cast_ids) {
    $.ajax({
      type: "GET",
      url: "/api/tmdb/person/" + movie_cast.cast_ids[cast_id],
      async: false,
      success: function (cast_details) {
        cast_bdays.push(
          cast_details.birthday
            ? new Date(cast_details.birthday)
                .toDateString()
                .split(" ")
                .slice(1)
                .join(" ")
            : "Unknown",
        );
        cast_bios.push(cast_details.biography || "No biography available");
        cast_places.push(cast_details.place_of_birth || "Unknown");
      },
    });
  }
  return {
    cast_bdays: cast_bdays,
    cast_bios: cast_bios,
    cast_places: cast_places,
  };
}

// getting the details of the cast for the requested movie (via backend proxy)
function get_movie_cast(movie_id) {
  cast_ids = [];
  cast_names = [];
  cast_chars = [];
  cast_profiles = [];

  $.ajax({
    type: "GET",
    url: "/api/tmdb/movie/" + movie_id + "/credits",
    async: false,
    success: function (my_movie) {
      if (my_movie.cast && my_movie.cast.length > 0) {
        var top_cast =
          my_movie.cast.length >= 10
            ? [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            : [0, 1, 2, 3, 4];
        for (var i = 0; i < top_cast.length; i++) {
          if (my_movie.cast[i]) {
            cast_ids.push(my_movie.cast[i].id);
            cast_names.push(my_movie.cast[i].name);
            cast_chars.push(my_movie.cast[i].character);
            cast_profiles.push(
              my_movie.cast[i].profile_path
                ? "https://image.tmdb.org/t/p/original" +
                    my_movie.cast[i].profile_path
                : "https://via.placeholder.com/240x360?text=No+Image",
            );
          }
        }
      }
    },
    error: function () {
      console.log("Error fetching cast");
    },
  });

  return {
    cast_ids: cast_ids,
    cast_names: cast_names,
    cast_chars: cast_chars,
    cast_profiles: cast_profiles,
  };
}

// getting posters for all the recommended movies (via backend proxy)
function get_movie_posters(arr) {
  var arr_poster_list = [];
  for (var m in arr) {
    $.ajax({
      type: "GET",
      url: "/api/tmdb/search?query=" + encodeURIComponent(arr[m]),
      async: false,
      success: function (m_data) {
        if (
          m_data.results &&
          m_data.results[0] &&
          m_data.results[0].poster_path
        ) {
          arr_poster_list.push(
            "https://image.tmdb.org/t/p/original" +
              m_data.results[0].poster_path,
          );
        } else {
          arr_poster_list.push(
            "https://via.placeholder.com/240x360?text=No+Poster",
          );
        }
      },
      error: function () {
        arr_poster_list.push(
          "https://via.placeholder.com/240x360?text=No+Poster",
        );
      },
    });
  }
  return arr_poster_list;
}
