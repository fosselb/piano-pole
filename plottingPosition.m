% plottingPosition.m
% Authors: Fosse Lin-Bianco and Evan Mitchell
% Purpose: Getting raw acceleration and gyroscope data from MPU-6050
% senor. Performing integration algorithm to determine velocity and
% position

clc;
close all;
clear;
format compact;

gravity_in_meters_per_second = 9.80665;

T = readtable('log.csv');

t = table2array(T(:, 1));
ax = table2array(T(:, 2)) * gravity_in_meters_per_second; % m/s^2
ay = table2array(T(:, 3)) * gravity_in_meters_per_second; % m/s^2
az = table2array(T(:, 4)) * gravity_in_meters_per_second; % m/s^2

vx = cumtrapz(t, ax);
vy = cumtrapz(t, ay);
vz = cumtrapz(t, az);

px = cumtrapz(t, vx);
py = cumtrapz(t, vy);
pz = cumtrapz(t, vz);

% 2D data plot
figure;
subplot(3, 1, 1);
plot(t, az);
title("Acceleration Data from MPU-6050 Module");
xlabel("time (sec)");
ylabel("Accel Z (m/s^2)");

subplot(3, 1, 2);
plot(t, vz);
xlabel("time (sec)");
title("Velocity Data from MPU-6050 Module");
ylabel("Velocity Z (m/s)");

subplot(3, 1, 3);
plot(t, pz);
xlabel("time (sec)");
title("Position Data from MPU-6050 Module");
ylabel("Position Z (m)");

% 3D data plot
figure;
subplot(3, 1, 1);
% plot3(ax, ay, az, 'o', ax(end), ay(end), az(end), 'or');
scatter3(ax, ay, az, 40, t);
colorbar;
title("Acceleration Data from MPU-6050 Module");
xlabel("X (m/s^2)");
ylabel("Y (m/s^2)");
zlabel("Z (m/s^2)");

% figure;
subplot(3, 1, 2);
% plot3(vx, vy, vz, 'o', vx(end), vy(end), vz(end), 'or');
scatter3(vx, vy, vz, 40, t);
colorbar;
title("Velocity Data from MPU-6050 Module");
xlabel("X (m/s)");
ylabel("Y (m/s)");
zlabel("Z (m/s)");

% figure;
subplot(3, 1, 3);
% plot3(px, py, pz, 'o', px(end), py(end), pz(end), 'or');
scatter3(px, py, pz, 40, t);
colorbar;
title("Position Data from MPU-6050 Module");
xlabel("X (m)");
ylabel("Y (m)");
zlabel("Z (m)");