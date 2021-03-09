% plottingPosition.m
% Authors: Fosse Lin-Bianco and Evan Mitchell
% Purpose: Getting acceleration data from BNO085 sensor. Performing
% integration algorithm to determine velocity and position.

clear; clc;
close all;


T = readtable("../logBNO085-stability.csv");

t = table2array(T(:, 1));
t = t - t(1);

quat = quaternion(table2array(T(:, 6:9)));
acc = table2array(T(:, 2:4));
accr = rotatepoint(quat, acc);

stability = table2array(T(:, 12));
accr = accr.*((stability<1|stability>3)*[1, 1, 1]);

vel = cumtrapz(t, acc);
velr = cumtrapz(t, accr);

velr = velr.*((stability<1|stability>3)*[1, 1, 1]);

pos = cumtrapz(t, vel);
posr = cumtrapz(t, velr);

% posr = posr - (t>15)*posr(1370, :) + (t>15)*[-0.1, 0.4, -0.2];

% 2D data plot
figure;
subplot(3, 1, 1);
plot(t, acc(:,3));
title("Acceleration Data from BNO085");
xlabel("time (s)");
ylabel("Accel Z (m/s^2)");

subplot(3, 1, 2);
plot(t, vel(:,3));
xlabel("time (s)");
title("Velocity Data from BNO085");
ylabel("Velocity Z (m/s)");

subplot(3, 1, 3);
plot(t, pos(:,3));
xlabel("time (s)");
title("Position Data from BNO085");
ylabel("Position Z (m)");


% % 3D data plot
% figure;
% subplot(3, 1, 1);
% scatter3(acc(:,1), acc(:,2), acc(:,3), 40, t);
% colorbar;
% title("Acceleration Data from MPU-6050 Module");
% xlabel("X (m/s^2)");
% ylabel("Y (m/s^2)");
% zlabel("Z (m/s^2)");

% subplot(3, 1, 2);
% scatter3(vel(:,1), vel(:,2), vel(:,3), 40, t);
% colorbar;
% title("Velocity Data from MPU-6050 Module");
% xlabel("X (m/s)");
% ylabel("Y (m/s)");
% zlabel("Z (m/s)");

% subplot(3, 1, 3);
% scatter3(pos(:,1), pos(:,2), pos(:,3), 40, t);
% colorbar;
% title("Position Data from MPU-6050 Module");
% xlabel("X (m)");
% ylabel("Y (m)");
% zlabel("Z (m)");


% 3D data plot
figure;
subplot(3, 1, 1);
scatter3(accr(:,1), accr(:,2), accr(:,3), 40, t);
colorbar;
title("Acceleration Data from BNO085");
xlabel("X (m/s^2)");
ylabel("Y (m/s^2)");
zlabel("Z (m/s^2)");

subplot(3, 1, 2);
scatter3(velr(:,1), velr(:,2), velr(:,3), 40, t);
colorbar;
title("Velocity Data from BNO085");
xlabel("X (m/s)");
ylabel("Y (m/s)");
zlabel("Z (m/s)");

subplot(3, 1, 3);
scatter3(posr(:,1), posr(:,2), posr(:,3), 40, t);
colorbar;
title("Position Data from BNO085");
xlabel("X (m)");
ylabel("Y (m)");
zlabel("Z (m)");
%
% a2 = smoothdata(accr, 'movmedian', 3);
% v2 = cumtrapz(t, a2);
% p2 = cumtrapz(t, v2);
%
% % 3D data plot
% figure;
% subplot(3, 1, 1);
% scatter3(a2(:,1), a2(:,2), a2(:,3), 40, t);
% colorbar;
% title("Acceleration Data from BNO085");
% xlabel("X (m/s^2)");
% ylabel("Y (m/s^2)");
% zlabel("Z (m/s^2)");
%
% subplot(3, 1, 2);
% scatter3(v2(:,1), v2(:,2), v2(:,3), 40, t);
% colorbar;
% title("Velocity Data from BNO085");
% xlabel("X (m/s)");
% ylabel("Y (m/s)");
% zlabel("Z (m/s)");
%
% subplot(3, 1, 3);
% scatter3(p2(:,1), p2(:,2), p2(:,3), 40, t);
% colorbar;
% title("Position Data from BNO085");
% xlabel("X (m)");
% ylabel("Y (m)");
% zlabel("Z (m)");


% fig = figure;
% fig.Position = [0, 0, 560, 840];
% subplot(3, 1, 1);
% view(3);
% grid on;
% title("Acceleration");
% xlabel("X (m/s^2)");
% ylabel("Y (m/s^2)");
% zlabel("Z (m/s^2)");
% axis([min(accr(:,1)), max(accr(:,1)), min(accr(:,2)), max(accr(:,2)), min(accr(:,3)), max(accr(:,3))]);
% hold on;
% subplot(3, 1, 2);
% view(3);
% grid on;
% title("Velocity");
% xlabel("X (m/s)");
% ylabel("Y (m/s)");
% zlabel("Z (m/s)");
% axis([min(velr(:,1)), max(velr(:,1)), min(velr(:,2)), max(velr(:,2)), min(velr(:,3)), max(velr(:,3))]);
% hold on;
% subplot(3, 1, 3);
% view(3);
% grid on;
% title("Position");
% xlabel("X (m)");
% ylabel("Y (m)");
% zlabel("Z (m)");
% axis([min(posr(:,1)), max(posr(:,1)), min(posr(:,2)), max(posr(:,2)), min(posr(:,3)), max(posr(:,3))]);
% hold on;
%
% last_t = t(1);
% last_k = 1;
% writer = VideoWriter("vid.mp4", "MPEG-4");
% writer.FrameRate = 10;
% open(writer);
% for k=1:length(t)
%     if t(k) - last_t < 1/writer.FrameRate
%         continue
%     end
%
%     figure(fig);
%
%     subplot(3, 1, 1);
%     scatter3(accr(last_k:k-1,1), accr(last_k:k-1,2), accr(last_k:k-1,3), 20, t(last_k:k-1), "filled");
%
%     subplot(3, 1, 2);
%     scatter3(velr(last_k:k-1,1), velr(last_k:k-1,2), velr(last_k:k-1,3), 20, t(last_k:k-1), "filled");
%
%     subplot(3, 1, 3);
%     scatter3(posr(last_k:k-1,1), posr(last_k:k-1,2), posr(last_k:k-1,3), 20, t(last_k:k-1), "filled");
%
%     drawnow
%     frame = getframe(fig);
%     writeVideo(writer, frame);
%     last_t = last_t + 1/writer.FrameRate;
%     last_k = k;
% end
% close(writer)
