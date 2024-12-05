import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import * as L from 'leaflet';

@Component({
  selector: 'app-map',
  templateUrl: './map.component.html',
  styleUrls: ['./map.component.css'] // Correct the `styleUrl` typo to `styleUrls`.
})
export class MapComponent {
  private map: any;
  private geoJsonData: any;

  constructor(public http: HttpClient) {}

  private getGeoJson(): Promise<any> {
    return this.http.get("./MapTiles.geojson").toPromise();
  }

  private async initMap(): Promise<void> {
    this.map = L.map('map', {
      center: [45.795, 24.676],
      zoom: 8
    });

    const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 15,
      minZoom: 3,
      attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    });

    tiles.addTo(this.map);

    if (this.geoJsonData) {
      L.geoJSON(this.geoJsonData).addTo(this.map);
    } else {
      console.error('GeoJSON data is not loaded.');
    }
  }

  async ngAfterViewInit(): Promise<void> {
    try {
      this.geoJsonData = await this.getGeoJson();
      this.initMap();
    } catch (error) {
      console.error('Failed to load GeoJSON data:', error);
    }
  }
}
