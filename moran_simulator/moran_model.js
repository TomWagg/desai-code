/* 
================================================================================
    Created by Tom Wagg in June 2019 whilst working with Michael Desai Lab at Harvard
================================================================================
*/

const N = 10;
const MAX_PLOTS = 3;
let XAXIS = range(0, 1);
let n = N / 2;
let t = 0;

const config = {
    type: 'line',
    data: {
        labels: XAXIS,
    },
    options: {
        responsive: true,
        animation: {
            duration: 0
        },
        hover: {
            animationDuration: 0
        },
        responsiveAnimationDuration: 0,
        tooltips: {
            mode: 'point',
            intersect: false,
        },
        hover: {
            mode: 'nearest',
            intersect: true
        },
        legend: {
            display: false,
        },
        scales: {
            xAxes: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Time'
                }
            }],
            yAxes: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Count'
                }
            }]
        }
    }
};

$(function () {

    let ctx = document.getElementById('canvas').getContext('2d');
    window.myLine = new Chart(ctx, config);

    document.getElementById("new_run").addEventListener('click', new_run);
    document.getElementById("reset").addEventListener('click', function () {
        $("#start_count").val(N / 2);
        $("#fitness").val(0);
        $("#mutation_mu").val(0);
        $("#mutation_nu").val(0);
        $(".linked-input").trigger("input");
    });
    document.getElementById("clear").addEventListener("click", function () {
        config.data.datasets.length = 0;
        config.data.labels = [0];
        window.myLine.update();
    })

    $(".linked-input").on("input", function () {
        $("#" + this.getAttribute("data-linked")).val(this.value);
    });

    $(".linked-input").on("blur", function () {
        this.value = parseInt(this.value) > parseInt(this.max) ? this.max : this.value;
    });

    $("#main-carousel").carousel({
        interval: false,
        keyboard: false,
        touch: false
    });
    $("#help_link").on("click", function () {
        $("#main-carousel").carousel(1);
    });
    $(".btn-back").on("click", function () {
        $("#main-carousel").carousel(0);
    });
    new_run();
});

function new_run() {
    document.getElementById("new_run").disabled = true;
    $(".linked-input").trigger("blur");

    n0 = parseFloat($("#start_count_typing").val());
    s = parseFloat($("#fitness_typing").val());
    mu = parseFloat($("#mutation_mu_typing").val());
    nu = parseFloat($("#mutation_nu_typing").val());

    console.log(s, document.getElementById("fitness_typing"), $("#fitness_typing").val());

    t = 0;
    n = n0;

    // if there are too many then remove one
    if (config.data.datasets.length + 1 > MAX_PLOTS) {
        remove_oldest_line();
    }

    // create new dataset
    config.data.datasets.push({
        label: "s: " + s + ", \u03BC: " + mu + ", \u03BD: " + nu + ", n",
        borderColor: 'rgb(' + Math.round(Math.random() * 255) + "," + Math.round(Math.random() * 255) + "," + Math.round(Math.random() * 255) + ')',
        data: [n0],
        fill: false,
    });

    // start adding data
    const last = config.data.datasets.length - 1;

    function step(timestamp) {
        if (n <= 0 || n >= N || t > 499) {
            document.getElementById("new_run").disabled = false;
        } else {
            update_data(last, s, mu, nu);
            window.requestAnimationFrame(step);
        }
    }

    console.log(window.requestAnimationFrame(step));
}

function update_data(dataset = 0, s = 0, mu = 0, nu = 0) {
    // stretch x-axis
    t += 1;
    if (config.data.labels[config.data.labels.length - 1] < t) {
        config.data.labels.push(t);
    }

    // THE MODELLY BIT
    const mean_fitness = (n * (1 + s) + (N - n)) / N
    const up = (n * (1 + s) * (1 - mu) * (N - n) + (N - n) * nu * (N - n)) / (N ** 2 * mean_fitness);
    const down = ((N - n) * (1 - nu) * n + n * (1 + s) * mu * n) / (N ** 2 * mean_fitness);
    const same = 1 - up - down;

    n += chance.weighted([1, 0, -1], [up, same, down])
    config.data.datasets[dataset].data.push(n);

    window.myLine.update();
}

function remove_oldest_line() {
    config.data.datasets.shift();
    let max_t = 0;
    for (let i = 0; i < config.data.datasets.length; i++) {
        max_t = config.data.datasets[i].data.length > max_t ? config.data.datasets[i].data.length : max_t;
    }
    config.data.labels = range(0, max_t);
}

function range(start, stop, step) {
    if (typeof stop == 'undefined') {
        // one param defined
        stop = start;
        start = 0;
    }

    if (typeof step == 'undefined') {
        step = 1;
    }

    if ((step > 0 && start >= stop) || (step < 0 && start <= stop)) {
        return [];
    }

    var result = [];
    for (var i = start; step > 0 ? i < stop : i > stop; i += step) {
        result.push(i);
    }

    return result;
};