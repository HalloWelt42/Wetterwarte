// Einstieg der Telefonansicht (telefon.html). Eigenes Bündel: kein gridstack, MapLibre erst im Karten-Reiter.
import "@fontsource/barlow/400.css";
import "@fontsource/barlow/500.css";
import "@fontsource/barlow/600.css";
import "@fontsource/barlow/700.css";
import "@fortawesome/fontawesome-free/css/all.min.css";
import "./seite.css";
import "./telefon.css";

import { mount } from "svelte";
import Telefon from "./Telefon.svelte";

mount(Telefon, { target: document.getElementById("telefon")! });
